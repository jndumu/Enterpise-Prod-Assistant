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
    from fastapi import FastAPI, HTTPException, WebSocket
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    raise ImportError("Please install fastapi uvicorn: pip install fastapi uvicorn")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.mcp.client import MCPClient

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
            title="MCP Semantic Search Server",
            description="Production-ready semantic search with web fallback",
            version="1.0.0"
        )
        
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
        
        @self.app.get("/")
        async def root():
            return {"message": "MCP Semantic Search Server", "status": "running"}
        
        @self.app.get("/health")
        async def health_check():
            status = self.client.get_system_status()
            return {"status": "healthy", "components": status}
        
        @self.app.post("/query", response_model=QueryResponse)
        async def query(request: QueryRequest):
            try:
                # Update threshold if provided
                if request.threshold:
                    self.client.threshold = request.threshold
                
                result = self.client.query(request.question)
                result["timestamp"] = datetime.now().isoformat()
                
                return QueryResponse(**result)
                
            except Exception as e:
                logger.error(f"Query error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
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
    server = MCPServer(**kwargs)
    server.run()

if __name__ == "__main__":
    start_server()