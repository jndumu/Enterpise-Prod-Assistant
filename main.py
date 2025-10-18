"""
Enterprise Production Assistant - AI-powered Document Q&A System

A minimal, production-ready FastAPI application that:
1. Accepts PDF document uploads
2. Processes and stores documents in memory
3. Answers questions using uploaded documents
4. Falls back to web search when needed
5. Provides a clean web interface for users

Architecture:
- FastAPI backend with automatic API documentation
- In-memory document storage (production would use vector DB)
- Simple keyword-based document search
- DuckDuckGo web search fallback
- Responsive HTML frontend with inline CSS/JS
"""

# === IMPORTS ===
import os
import hashlib
import io
from typing import Dict, Any, Optional
from datetime import datetime

# FastAPI framework
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# Document processing
from pypdf import PdfReader
import requests
from dotenv import load_dotenv

# === CONFIGURATION ===
load_dotenv()  # Load environment variables

# Initialize FastAPI application
app = FastAPI(
    title="Enterprise Production Assistant",
    description="AI-powered document Q&A system with web search fallback",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# Setup template engine and static files
templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# === DATA STORAGE ===
# In-memory document storage (production would use persistent vector database)
documents: Dict[str, Dict] = {}

# === DATA MODELS ===

class QueryRequest(BaseModel):
    """Request model for API questions."""
    question: str

# === API ENDPOINTS ===

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Home page - serves the main web interface.
    
    Returns:
        HTML page with document upload and Q&A interface
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: System status and document count
    """
    return {
        "status": "healthy", 
        "documents_loaded": len(documents),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """
    Upload and process PDF documents.
    
    Args:
        file: PDF file to upload and process
        
    Returns:
        dict: Success status, message, and document ID
        
    Process:
        1. Validates file is PDF
        2. Extracts text from all pages
        3. Generates unique document ID
        4. Stores in memory for searching
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            return {"success": False, "error": "Only PDF files supported"}
        
        # Process PDF document
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        
        # Extract text from all pages
        text = "".join([page.extract_text() for page in pdf_reader.pages])
        
        # Generate unique document ID
        doc_id = hashlib.md5(content).hexdigest()[:8]
        
        # Store document in memory
        documents[doc_id] = {
            "filename": file.filename,
            "text": text,
            "pages": len(pdf_reader.pages),
            "uploaded_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": f"Uploaded {file.filename} ({len(pdf_reader.pages)} pages)",
            "document_id": doc_id,
            "pages_processed": len(pdf_reader.pages)
        }
        
    except Exception as e:
        return {"success": False, "error": f"Upload failed: {str(e)}"}

@app.post("/query")
async def query(request: Optional[QueryRequest] = None, question: str = Form(None)):
    """
    Answer questions using uploaded documents or web search.
    
    Args:
        request: JSON request with question (for API calls)
        question: Form data with question (for web interface)
        
    Returns:
        dict: Answer, source, confidence score, and metadata
        
    Search Strategy:
        1. Search uploaded documents first (keyword matching)
        2. Fall back to DuckDuckGo web search
        3. Provide helpful fallback message if no results
    """
    try:
        # Extract question from either JSON or form data
        q = request.question if request else question
        if not q:
            return {"success": False, "error": "No question provided"}
        
        # STEP 1: Search uploaded documents first
        for doc_id, doc in documents.items():
            # Simple keyword matching (production would use vector search)
            if any(word.lower() in doc["text"].lower() for word in q.split()):
                # Find most relevant line
                lines = doc["text"].split('\n')
                for line in lines:
                    if any(word.lower() in line.lower() for word in q.split()) and len(line.strip()) > 20:
                        return {
                            "success": True,
                            "answer": line[:500] + "..." if len(line) > 500 else line,
                            "source": "uploaded_document",
                            "filename": doc["filename"],
                            "confidence": 0.8,
                            "timestamp": datetime.now().isoformat()
                        }
        
        # STEP 2: Fallback to web search using DuckDuckGo
        try:
            search_url = f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(search_url, timeout=5)
            data = response.json()
            
            if data.get("Abstract"):
                return {
                    "success": True,
                    "answer": data["Abstract"],
                    "source": "web_search",
                    "confidence": 0.7,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception:
            pass  # Web search failed, continue to fallback
        
        # STEP 3: Default helpful response
        return {
            "success": True,
            "answer": "I don't have specific information about that. Try uploading a relevant document or rephrasing your question.",
            "source": "fallback",
            "confidence": 0.3,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": f"Query failed: {str(e)}"}

# === APPLICATION STARTUP ===
if __name__ == "__main__":
    """
    Run the application server.
    
    Access points:
    - Web Interface: http://localhost:8000
    - API Documentation: http://localhost:8000/docs
    - Health Check: http://localhost:8000/health
    """
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
