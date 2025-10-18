"""
Document processing service
"""

import hashlib
import io
from typing import Dict
from datetime import datetime
from pypdf import PdfReader

from ..core.exceptions import DocumentProcessingError
from ..models.schemas import DocumentInfo

class DocumentProcessor:
    """Service for processing PDF documents"""
    
    def __init__(self):
        self.documents: Dict[str, DocumentInfo] = {}
    
    def process_pdf(self, content: bytes, filename: str) -> DocumentInfo:
        """Process PDF and extract text"""
        try:
            pdf_reader = PdfReader(io.BytesIO(content))
            text = "".join([page.extract_text() for page in pdf_reader.pages])
            
            doc_id = hashlib.md5(content).hexdigest()[:8]
            
            doc_info = DocumentInfo(
                filename=filename,
                text=text,
                pages=len(pdf_reader.pages),
                uploaded_at=datetime.now().isoformat(),
                doc_id=doc_id
            )
            
            self.documents[doc_id] = doc_info
            return doc_info
            
        except Exception as e:
            raise DocumentProcessingError(f"Failed to process PDF: {str(e)}")
    
    def search_documents(self, query: str) -> Dict:
        """Search through uploaded documents"""
        query_words = set(query.lower().split())
        
        for doc_id, doc in self.documents.items():
            if any(word in doc.text.lower() for word in query_words):
                lines = doc.text.split('\n')
                for line in lines:
                    if any(word in line.lower() for word in query_words) and len(line.strip()) > 20:
                        return {
                            "answer": line[:500] + "..." if len(line) > 500 else line,
                            "source": "document",
                            "filename": doc.filename,
                            "confidence": 0.85
                        }
        return None