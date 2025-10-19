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

# Conversation memory for follow-up questions
conversation_history: Dict[str, list] = {}  # session_id -> [conversation]

# Content moderation keywords
HARMFUL_KEYWORDS = [
    'violence', 'harmful', 'illegal', 'explicit', 'inappropriate', 'offensive',
    'hate', 'discrimination', 'abuse', 'threat', 'dangerous', 'toxic'
]

PROFANITY_FILTER = [
    # Basic content filter - add more as needed
    'spam', 'scam', 'fraud'
]

# === DATA MODELS ===

class QueryRequest(BaseModel):
    """Request model for API questions."""
    question: str
    session_id: Optional[str] = None

# === UTILITY FUNCTIONS ===

def moderate_content(text: str) -> tuple[bool, str]:
    """
    Check content for inappropriate material.
    
    Returns:
        tuple: (is_safe: bool, reason: str)
    """
    text_lower = text.lower()
    
    # Check for harmful keywords
    for keyword in HARMFUL_KEYWORDS:
        if keyword in text_lower:
            return False, f"Content contains inappropriate material: {keyword}"
    
    # Check for profanity
    for word in PROFANITY_FILTER:
        if word in text_lower:
            return False, f"Content contains filtered language: {word}"
    
    # Additional safety checks
    if len(text) > 2000:
        return False, "Question too long (max 2000 characters)"
    
    if text.count('http') > 5 or text.count('www') > 3:
        return False, "Too many URLs detected"
    
    return True, "Content is safe"

def get_conversation_context(session_id: str, max_history: int = 3) -> str:
    """
    Get conversation context for follow-up questions.
    
    Args:
        session_id: Session identifier
        max_history: Maximum number of previous exchanges to include
    
    Returns:
        str: Formatted conversation context
    """
    if session_id not in conversation_history:
        return ""
    
    history = conversation_history[session_id][-max_history:]
    context = ""
    
    for i, exchange in enumerate(history):
        context += f"Previous Q{i+1}: {exchange['question']}\n"
        context += f"Previous A{i+1}: {exchange['answer'][:200]}...\n\n"
    
    return context

def store_conversation(session_id: str, question: str, answer: str, source: str):
    """
    Store conversation exchange in memory.
    
    Args:
        session_id: Session identifier
        question: User's question
        answer: System's answer
        source: Source of the answer
    """
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    conversation_history[session_id].append({
        "question": question,
        "answer": answer,
        "source": source,
        "timestamp": datetime.now().isoformat()
    })
    
    # Keep only last 10 exchanges per session
    if len(conversation_history[session_id]) > 10:
        conversation_history[session_id] = conversation_history[session_id][-10:]

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

@app.get("/debug/documents")
async def debug_documents():
    """
    Debug endpoint to check document storage.
    
    Returns:
        dict: Document information for debugging
    """
    doc_info = []
    for doc_id, doc in documents.items():
        doc_info.append({
            "id": doc_id,
            "filename": doc["filename"],
            "pages": doc["pages"],
            "word_count": doc["word_count"],
            "text_preview": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"],
            "uploaded_at": doc["uploaded_at"]
        })
    
    return {
        "total_documents": len(documents),
        "documents": doc_info
    }

@app.get("/debug/conversations")
async def debug_conversations():
    """
    Debug endpoint to check conversation history.
    
    Returns:
        dict: Conversation history for debugging
    """
    conv_info = []
    for session_id, history in conversation_history.items():
        conv_info.append({
            "session_id": session_id,
            "exchange_count": len(history),
            "last_activity": history[-1]["timestamp"] if history else None,
            "recent_questions": [h["question"][:100] for h in history[-3:]]  # Last 3 questions
        })
    
    return {
        "total_sessions": len(conversation_history),
        "total_exchanges": sum(len(h) for h in conversation_history.values()),
        "sessions": conv_info
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
        
        # Extract and clean text from all pages
        raw_text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                # Clean up text formatting
                page_text = page_text.replace('\n\n', '\n').replace('\t', ' ')
                raw_text += page_text + "\n"
        
        # Clean and normalize text
        text = ' '.join(raw_text.split())  # Remove extra whitespace
        
        # Generate unique document ID
        doc_id = hashlib.md5(content).hexdigest()[:8]
        
        # Store document with metadata
        documents[doc_id] = {
            "filename": file.filename,
            "text": text,
            "raw_text": raw_text,  # Keep original formatting for context
            "pages": len(pdf_reader.pages),
            "word_count": len(text.split()),
            "uploaded_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": f"Uploaded {file.filename} ({len(pdf_reader.pages)} pages)",
            "document_id": doc_id,
            "pages_processed": len(pdf_reader.pages),
            "word_count": len(text.split())
        }
        
    except Exception as e:
        return {"success": False, "error": f"Upload failed: {str(e)}"}

@app.post("/query")
async def query(request: Optional[QueryRequest] = None, question: str = Form(None), session_id: str = Form(None)):
    """
    Answer questions using uploaded documents or web search.
    Enhanced with conversation memory and content moderation.
    
    Args:
        request: JSON request with question (for API calls)
        question: Form data with question (for web interface)
        session_id: Session ID for conversation tracking
        
    Returns:
        dict: Answer, source, confidence score, and metadata
        
    Search Strategy:
        1. Content moderation check
        2. Search uploaded documents with conversation context
        3. Fall back to DuckDuckGo web search
        4. Provide helpful fallback message if no results
    """
    try:
        # Extract question and session from either JSON or form data
        q = request.question if request else question
        sid = request.session_id if request and request.session_id else session_id or "default"
        
        if not q:
            return {"success": False, "error": "No question provided"}
        
        # STEP 0: Content moderation
        is_safe, moderation_reason = moderate_content(q)
        if not is_safe:
            return {
                "success": False, 
                "error": f"Content moderation: {moderation_reason}",
                "moderated": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # Get conversation context for follow-up questions
        context = get_conversation_context(sid)
        enhanced_query = f"{context}Current question: {q}" if context else q
        
        print(f"DEBUG: Session {sid} - Enhanced query with context: {len(context)} chars context")  # Debug log
        
        # STEP 1: Search uploaded documents with robust matching
        best_match = None
        best_score = 0
        
        print(f"DEBUG: Searching {len(documents)} documents for: '{q}'")  # Debug log
        
        for doc_id, doc in documents.items():
            print(f"DEBUG: Checking document {doc['filename']} with {doc['word_count']} words")  # Debug log
            
            # Enhanced text processing - more inclusive word filtering
            doc_text = doc["text"].lower()
            question_words = [word.lower().strip('.,!?;:"()[]') for word in q.split() if len(word) > 1]  # Changed from >2 to >1
            
            print(f"DEBUG: Question words: {question_words}")  # Debug log
            
            # Multiple text chunking strategies for better matching
            text_chunks = []
            
            # Strategy 1: Split by sentences (periods, exclamation, question marks)
            sentences = [s.strip() for s in doc["text"].replace('\n', ' ').replace('!', '.').replace('?', '.').split('.') if len(s.strip()) > 20]
            text_chunks.extend(sentences)
            
            # Strategy 2: Split by paragraphs (double newlines in raw text)
            paragraphs = [p.strip() for p in doc["raw_text"].split('\n\n') if len(p.strip()) > 50]
            text_chunks.extend(paragraphs)
            
            # Strategy 3: Fixed-size chunks for very long documents
            words = doc["text"].split()
            if len(words) > 100:
                chunk_size = 50
                for i in range(0, len(words), chunk_size):
                    chunk = ' '.join(words[i:i+chunk_size*2])  # Overlapping chunks
                    if len(chunk) > 100:
                        text_chunks.append(chunk)
            
            print(f"DEBUG: Generated {len(text_chunks)} text chunks")  # Debug log
            
            # Search through all text chunks
            for chunk in text_chunks:
                chunk_lower = chunk.lower()
                
                # Multiple matching strategies
                matches = 0
                total_words = len(question_words)
                
                # Exact word matches
                exact_matches = sum(1 for word in question_words if word in chunk_lower)
                
                # Partial word matches (for stemming-like effects)
                partial_matches = 0
                for word in question_words:
                    if len(word) > 3:  # Only for longer words
                        word_stem = word[:len(word)-1]  # Remove last character
                        if word_stem in chunk_lower and word not in chunk_lower:
                            partial_matches += 0.5
                
                # Phrase matching bonus
                phrase_bonus = 0
                if len(question_words) >= 2:
                    question_phrase = ' '.join(question_words)
                    if question_phrase in chunk_lower:
                        phrase_bonus = 0.3
                
                # Calculate total relevance score
                total_matches = exact_matches + partial_matches + phrase_bonus
                
                if total_matches > 0:
                    # More lenient scoring
                    relevance_score = total_matches / max(total_words, 1)
                    
                    # Bonus factors
                    if len(chunk) > 100: relevance_score += 0.05
                    if exact_matches >= 2: relevance_score += 0.1
                    
                    # Lower threshold for better recall
                    if relevance_score > best_score and relevance_score > 0.1:  # Lowered from 0.3 to 0.1
                        best_score = relevance_score
                        best_match = {
                            "answer": chunk[:1000] + "..." if len(chunk) > 1000 else chunk,
                            "filename": doc["filename"],
                            "confidence": min(0.95, relevance_score * 0.8 + 0.2),  # More conservative confidence
                            "matches": exact_matches,
                            "relevance": relevance_score
                        }
                        print(f"DEBUG: New best match found - Score: {relevance_score:.3f}, Matches: {exact_matches}")  # Debug log
        
        # Return best document match if found
        if best_match:
            print(f"DEBUG: Returning document match with confidence {best_match['confidence']:.3f}")  # Debug log
            
            response = {
                "success": True,
                "answer": best_match["answer"],
                "source": "uploaded_document",
                "filename": best_match["filename"],
                "confidence": best_match["confidence"],
                "matches_found": best_match["matches"],
                "relevance_score": best_match["relevance"],
                "session_id": sid,
                "has_context": bool(context),
                "timestamp": datetime.now().isoformat()
            }
            
            # Store conversation for follow-up questions
            store_conversation(sid, q, best_match["answer"], "uploaded_document")
            
            return response
        
        print(f"DEBUG: No document matches found, trying web search...")  # Debug log
        
        # STEP 2: Fallback to web search using DuckDuckGo
        try:
            search_url = f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(search_url, timeout=5)
            data = response.json()
            
            if data.get("Abstract"):
                response = {
                    "success": True,
                    "answer": data["Abstract"],
                    "source": "web_search",
                    "confidence": 0.7,
                    "session_id": sid,
                    "has_context": bool(context),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Store conversation for follow-up questions
                store_conversation(sid, q, data["Abstract"], "web_search")
                
                return response
        except Exception:
            pass  # Web search failed, continue to fallback
        
        # STEP 3: Default helpful response
        fallback_answer = "I don't have specific information about that. Try uploading a relevant document or rephrasing your question."
        
        response = {
            "success": True,
            "answer": fallback_answer,
            "source": "fallback",
            "confidence": 0.3,
            "session_id": sid,
            "has_context": bool(context),
            "timestamp": datetime.now().isoformat()
        }
        
        # Store conversation for follow-up questions
        store_conversation(sid, q, fallback_answer, "fallback")
        
        return response
        
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
