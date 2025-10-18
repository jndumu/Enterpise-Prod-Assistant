"""
Pydantic models for Enterprise Production Assistant
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for questions"""
    question: str
    threshold: Optional[float] = 0.7

class QueryResponse(BaseModel):
    """Response model for answers"""
    success: bool
    answer: str
    source: str
    confidence: float
    filename: Optional[str] = None
    timestamp: str = datetime.now().isoformat()
    
class DocumentInfo(BaseModel):
    """Document information model"""
    filename: str
    text: str
    pages: int
    uploaded_at: str
    doc_id: str

class UploadResponse(BaseModel):
    """Upload response model"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    document_id: Optional[str] = None