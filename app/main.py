"""
Minimal Enterprise Production Assistant - Complete AI Q&A system in one file.
Under 100 lines with document upload, search, and web fallback.
"""

import os
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# FastAPI imports
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# Document processing
from pypdf import PdfReader
import io
import requests

# Load environment
load_dotenv()

app = FastAPI(title="Enterprise Assistant", version="1.0")
templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# In-memory storage
documents: Dict[str, Dict] = {}

class QueryRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("minimal.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "healthy", "documents": len(documents)}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            return {"success": False, "error": "Only PDF files supported"}
        
        # Process PDF
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        text = "".join([page.extract_text() for page in pdf_reader.pages])
        
        # Store document
        doc_id = hashlib.md5(content).hexdigest()[:8]
        documents[doc_id] = {
            "filename": file.filename,
            "text": text,
            "uploaded_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": f"Uploaded {file.filename}",
            "document_id": doc_id
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/query")
async def query(request: Optional[QueryRequest] = None, question: str = Form(None)):
    try:
        q = request.question if request else question
        if not q:
            return {"success": False, "error": "No question provided"}
        
        # Search documents first
        for doc_id, doc in documents.items():
            if any(word.lower() in doc["text"].lower() for word in q.split()):
                # Find relevant chunk
                lines = doc["text"].split('\n')
                for line in lines:
                    if any(word.lower() in line.lower() for word in q.split()):
                        return {
                            "success": True,
                            "answer": line[:500] + "..." if len(line) > 500 else line,
                            "source": "uploaded_document",
                            "filename": doc["filename"],
                            "confidence": 0.8,
                            "timestamp": datetime.now().isoformat()
                        }
        
        # Fallback to web search using DuckDuckGo
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
        except:
            pass
        
        # Default response
        return {
            "success": True,
            "answer": "I don't have specific information about that. Try uploading a relevant document.",
            "source": "fallback",
            "confidence": 0.3,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)