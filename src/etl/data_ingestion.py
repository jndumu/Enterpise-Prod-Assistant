"""
Data ingestion module for Enterprise Production Assistant
Handles PDF processing and text extraction for the knowledge base
"""

import os
import hashlib
from typing import List, Dict, Any
from pathlib import Path
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)

class DataIngestion:
    """Handles document ingestion and processing"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.processed_docs = {}
    
    def ingest_pdf(self, file_path: str) -> Dict[str, Any]:
        """Ingest a single PDF file"""
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                
            pdf_reader = PdfReader(file_path)
            text_chunks = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text.strip():
                    chunks = self._chunk_text(text, chunk_size=500)
                    for chunk_id, chunk in enumerate(chunks):
                        text_chunks.append({
                            'content': chunk,
                            'page': page_num + 1,
                            'chunk_id': chunk_id,
                            'source': os.path.basename(file_path)
                        })
            
            doc_id = hashlib.md5(content).hexdigest()[:12]
            
            doc_info = {
                'doc_id': doc_id,
                'filename': os.path.basename(file_path),
                'total_pages': len(pdf_reader.pages),
                'total_chunks': len(text_chunks),
                'chunks': text_chunks
            }
            
            self.processed_docs[doc_id] = doc_info
            logger.info(f"Ingested {file_path}: {len(text_chunks)} chunks from {len(pdf_reader.pages)} pages")
            
            return doc_info
            
        except Exception as e:
            logger.error(f"Failed to ingest {file_path}: {str(e)}")
            raise
    
    def ingest_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Ingest all PDF files from a directory"""
        results = []
        pdf_files = list(Path(directory).glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
        
        for pdf_file in pdf_files:
            try:
                result = self.ingest_pdf(str(pdf_file))
                results.append(result)
            except Exception as e:
                logger.error(f"Skipping {pdf_file}: {str(e)}")
                continue
        
        return results
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into smaller chunks for better retrieval"""
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about processed documents"""
        total_docs = len(self.processed_docs)
        total_chunks = sum(doc['total_chunks'] for doc in self.processed_docs.values())
        total_pages = sum(doc['total_pages'] for doc in self.processed_docs.values())
        
        return {
            'total_documents': total_docs,
            'total_pages': total_pages,
            'total_chunks': total_chunks,
            'documents': list(self.processed_docs.keys())
        }