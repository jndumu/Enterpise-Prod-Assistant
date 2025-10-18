"""
MCP Client for Enterprise Production Assistant
Orchestrates document retrieval and web search with intelligent fallback
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...retriever.document_retriever import DocumentRetriever
from ...etl.data_ingestion import DataIngestion

logger = logging.getLogger(__name__)

class MCPClient:
    """Model Context Protocol Client for intelligent Q&A orchestration"""
    
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
        self.retriever = DocumentRetriever()
        self.ingestion = DataIngestion()
        
    def process_document(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Process and ingest a document"""
        try:
            # Save temporarily for processing
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            try:
                # Ingest document
                doc_info = self.ingestion.ingest_pdf(temp_path)
                
                # Add to retriever
                self.retriever.add_documents([doc_info])
                
                return {
                    'success': True,
                    'document_id': doc_info['doc_id'],
                    'filename': doc_info['filename'],
                    'pages': doc_info['total_pages'],
                    'chunks_count': doc_info['total_chunks']
                }
                
            finally:
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def query(self, question: str) -> Dict[str, Any]:
        """Process a query with document search and web fallback"""
        start_time = datetime.now()
        
        try:
            # Step 1: Search documents
            documents = self.retriever.semantic_search(question, top_k=3)
            
            if documents and documents[0].metadata.get('score', 0) >= self.threshold:
                best_match = documents[0]
                return {
                    'success': True,
                    'question': question,
                    'answer': best_match.page_content,
                    'source': 'document',
                    'confidence': best_match.metadata.get('score', 0),
                    'filename': best_match.metadata.get('source', ''),
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'metadata': {
                        'doc_id': best_match.metadata.get('doc_id'),
                        'page': best_match.metadata.get('page'),
                        'total_matches': len(documents)
                    }
                }
            
            # Step 2: Web search fallback (simplified)
            import requests
            try:
                response = requests.get(
                    f"https://api.duckduckgo.com/?q={question}&format=json&no_html=1",
                    timeout=5
                )
                data = response.json()
                
                if data.get("Abstract"):
                    return {
                        'success': True,
                        'question': question,
                        'answer': data["Abstract"],
                        'source': 'web',
                        'confidence': 0.75,
                        'processing_time': (datetime.now() - start_time).total_seconds(),
                        'metadata': {'search_method': 'duckduckgo'}
                    }
            except:
                pass
            
            # Step 3: No good answer found
            return {
                'success': True,
                'question': question,
                'answer': 'No relevant information found. Try uploading a document or rephrasing your question.',
                'source': 'none',
                'confidence': 0.0,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return {
                'success': False,
                'question': question,
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        retriever_stats = self.retriever.get_document_stats()
        ingestion_stats = self.ingestion.get_document_stats()
        
        return {
            'retriever_available': True,
            'web_search_available': True,
            'provider': 'keyword_search',
            'threshold': self.threshold,
            'timestamp': datetime.now().timestamp(),
            'document_stats': retriever_stats,
            'ingestion_stats': ingestion_stats
        }