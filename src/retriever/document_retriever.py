"""
Document retrieval system for Enterprise Production Assistant
Handles semantic search and document retrieval
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document class for retrieval results"""
    page_content: str
    metadata: Dict[str, Any]

class DocumentRetriever:
    """Handles document retrieval and semantic search"""
    
    def __init__(self):
        self.documents = {}
        self.embeddings = None  # Would integrate with vector DB in production
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add processed documents to the retriever"""
        for doc in documents:
            doc_id = doc.get('doc_id')
            self.documents[doc_id] = doc
            logger.info(f"Added document {doc_id} with {doc.get('total_chunks', 0)} chunks")
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Document]:
        """Perform semantic search (simplified keyword matching for now)"""
        results = []
        query_words = set(query.lower().split())
        
        for doc_id, doc in self.documents.items():
            for chunk in doc.get('chunks', []):
                content = chunk.get('content', '').lower()
                
                # Simple keyword matching (would use embeddings in production)
                matches = sum(1 for word in query_words if word in content)
                if matches > 0:
                    score = matches / len(query_words)
                    
                    result = Document(
                        page_content=chunk.get('content', ''),
                        metadata={
                            'source': chunk.get('source', ''),
                            'page': chunk.get('page', 0),
                            'chunk_id': chunk.get('chunk_id', 0),
                            'doc_id': doc_id,
                            'score': score
                        }
                    )
                    results.append(result)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.metadata.get('score', 0), reverse=True)
        return results[:top_k]
    
    def search_by_source(self, source: str, top_k: int = 10) -> List[Document]:
        """Search documents by source filename"""
        results = []
        
        for doc_id, doc in self.documents.items():
            if source.lower() in doc.get('filename', '').lower():
                for chunk in doc.get('chunks', []):
                    result = Document(
                        page_content=chunk.get('content', ''),
                        metadata={
                            'source': chunk.get('source', ''),
                            'page': chunk.get('page', 0),
                            'chunk_id': chunk.get('chunk_id', 0),
                            'doc_id': doc_id,
                            'score': 1.0
                        }
                    )
                    results.append(result)
        
        return results[:top_k]
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get retriever statistics"""
        total_docs = len(self.documents)
        total_chunks = sum(doc.get('total_chunks', 0) for doc in self.documents.values())
        
        return {
            'document_count': total_docs,
            'total_chunks': total_chunks,
            'collection_name': 'semantic_data'
        }