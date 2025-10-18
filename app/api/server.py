"""
MCP Server for handling HTTP/WebSocket requests.
Production-ready implementation under 150 lines.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, WebSocket, Request, Form, UploadFile, File
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    raise ImportError("Please install fastapi uvicorn jinja2: pip install fastapi uvicorn jinja2 python-multipart")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.client import MCPClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    threshold: Optional[float] = 0.7

class BatchQueryRequest(BaseModel):
    questions: list
    threshold: Optional[float] = 0.7

class QueryResponse(BaseModel):
    question: str
    answer: str
    source: str
    success: bool
    confidence: float
    processing_time: float
    metadata: Dict[str, Any] = {}
    timestamp: str

class MCPServer:
    """Production-ready MCP Server with REST API and WebSocket support."""
    
    def __init__(self, 
                 astra_token: Optional[str] = None,
                 astra_api_endpoint: Optional[str] = None,
                 api_key: Optional[str] = None,
                 provider: str = "groq",
                 host: str = "0.0.0.0",
                 port: int = 8000):
        
        self.host = host
        self.port = port
        
        # Initialize MCP client
        self.client = MCPClient(
            astra_token=astra_token,
            astra_api_endpoint=astra_api_endpoint,
            api_key=api_key,
            provider=provider
        )
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Enterprise Production Assistant",
            description="AI-powered document Q&A system with web search",
            version="1.0.0"
        )
        
        # Setup templates and static files
        self.templates = Jinja2Templates(directory="frontend/templates")
        self.app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root(request: Request):
            return self.templates.TemplateResponse("rag_interface.html", {"request": request})
        
        @self.app.get("/app", response_class=HTMLResponse)
        async def app_interface(request: Request):
            return self.templates.TemplateResponse("rag_interface.html", {"request": request})
        
        @self.app.get("/health")
        async def health_check():
            status = self.client.get_system_status()
            return {"status": "healthy", "components": status}
        
        @self.app.post("/query")
        async def query(request: QueryRequest = None, question: str = Form(None)):
            try:
                # Handle both JSON and form data
                if request:
                    query_text = request.question
                    threshold = request.threshold or 0.7
                elif question:
                    query_text = question
                    threshold = 0.7
                else:
                    raise HTTPException(status_code=400, detail="No question provided")
                
                # Update threshold if provided
                self.client.threshold = threshold
                
                result = self.client.query(query_text)
                result["timestamp"] = datetime.now().isoformat()
                
                return result
                
            except Exception as e:
                logger.error(f"Query error: {e}")
                return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}
        
        @self.app.post("/upload")
        async def upload_file(file: UploadFile = File(...)):
            try:
                if not file.filename.lower().endswith('.pdf'):
                    return {"success": False, "error": "Only PDF files are supported"}
                
                # Read file content
                content = await file.read()
                
                # Process the document through MCP client
                result = self.client.process_document(content, file.filename)
                
                return {
                    "success": True,
                    "message": f"Document '{file.filename}' processed successfully",
                    "document_id": result.get("document_id", "unknown"),
                    "chunks_processed": result.get("chunks_count", 0),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Upload error: {e}")
                return {
                    "success": False,
                    "error": f"Failed to process document: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
        
        @self.app.post("/batch-query")
        async def batch_query(request: BatchQueryRequest):
            try:
                # Update threshold if provided
                if request.threshold:
                    self.client.threshold = request.threshold
                
                results = self.client.batch_query(request.questions)
                
                # Add timestamps
                for result in results:
                    result["timestamp"] = datetime.now().isoformat()
                
                return {"results": results, "count": len(results)}
                
            except Exception as e:
                logger.error(f"Batch query error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            logger.info("WebSocket connection established")
            
            try:
                while True:
                    # Receive message from client
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    if message.get("type") == "query":
                        question = message.get("question", "")
                        threshold = message.get("threshold", 0.7)
                        
                        self.client.threshold = threshold
                        result = self.client.query(question)
                        result["timestamp"] = datetime.now().isoformat()
                        
                        await websocket.send_text(json.dumps(result))
                    
                    elif message.get("type") == "status":
                        status = self.client.get_system_status()
                        await websocket.send_text(json.dumps({
                            "type": "status",
                            "data": status,
                            "timestamp": datetime.now().isoformat()
                        }))
                    
                    else:
                        await websocket.send_text(json.dumps({
                            "error": "Unknown message type",
                            "timestamp": datetime.now().isoformat()
                        }))
                        
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.close()
    
    def run(self):
        """Start the MCP server."""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)
    
    async def async_run(self):
        """Start the MCP server asynchronously."""
        config = uvicorn.Config(self.app, host=self.host, port=self.port)
        server = uvicorn.Server(config)
        await server.serve()

# Convenience function to start server
def start_server(**kwargs):
    """Start MCP server with environment variables or provided arguments."""
    # Load environment variables with fallback to SSM parameters
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Try to get from environment variables first, then from SSM if in AWS
    config = {
        "astra_token": os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        "astra_api_endpoint": os.getenv("ASTRA_DB_API_ENDPOINT"), 
        "api_key": os.getenv("GROQ_API_KEY"),
        "provider": "groq"
    }
    
    # Override with any provided kwargs
    config.update(kwargs)
    
    # Remove None values
    config = {k: v for k, v in config.items() if v is not None}
    
    logger.info(f"Starting server with config keys: {list(config.keys())}")
    
    server = MCPServer(**config)
    server.run()

if __name__ == "__main__":
    start_server()
