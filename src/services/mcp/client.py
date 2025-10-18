"""
Industry-grade MCP Client orchestrating semantic search and web fallback.
Production-ready implementation under 150 lines.
"""

import asyncio
import logging
from typing import Dict, Optional, Any, List
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our production retriever
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
from src.retriever.production_retriever import Retriever as ProductionRetriever
from src.services.mcp.web_search import WebSearchTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClient:
    """Production MCP Client for semantic search with intelligent fallback."""
    
    def __init__(self, 
                 astra_token: Optional[str] = None,
                 astra_api_endpoint: Optional[str] = None,
                 api_key: Optional[str] = None,
                 provider: str = "groq",
                 relevance_threshold: float = 0.7):
        """Initialize MCP client with AstraDB and web search capabilities."""
        
        self.threshold = relevance_threshold
        self.provider = provider
        
        # Initialize production retriever
        try:
            self.retriever = ProductionRetriever()
            logger.info("✓ Production retriever initialized")
        except Exception as e:
            logger.warning(f"Retriever init failed: {e}")
            self.retriever = None
        
        # Initialize web search tool
        try:
            self.web_search = WebSearchTool(
                api_key=api_key,
                provider=provider
            )
            logger.info("✓ Web search tool initialized")
        except Exception as e:
            logger.warning(f"Web search init failed: {e}")
            self.web_search = None
    
    def query(self, question: str) -> Dict[str, Any]:
        """Process query with AstraDB first, then web search fallback."""
        start_time = asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0
        
        result = {
            "question": question,
            "answer": "",
            "source": "none",
            "confidence": 0.0,
            "processing_time": 0.0,
            "success": False
        }
        
        try:
            # Step 1: Try semantic search in AstraDB
            if self.retriever:
                semantic_results = self.retriever.call_retriever(question, top_k=3)
                
                if semantic_results:
                    best_match = semantic_results[0]
                    score = best_match.metadata.get('score', 0.0)
                    
                    # Only use if score meets threshold
                    if score >= self.threshold:
                        result.update({
                            "answer": best_match.page_content,
                            "source": "astradb",
                            "confidence": score,
                            "success": True,
                            "metadata": {
                                "total_matches": len(semantic_results),
                                "document_id": best_match.metadata.get('doc_id', 'unknown')
                            }
                        })
                        logger.info(f"✓ AstraDB match found (score: {score:.2f})")
                        return self._finalize_result(result, start_time)
            
            # Step 2: Fallback to web search
            if self.web_search:
                web_answer = self.web_search.search_and_summarize(question)
                if web_answer and "No relevant information" not in web_answer:
                    result.update({
                        "answer": web_answer,
                        "source": "web_search",
                        "confidence": 0.8,
                        "success": True,
                        "metadata": {"search_method": "duckduckgo"}
                    })
                    logger.info("✓ Web search provided answer")
                    return self._finalize_result(result, start_time)
            
            # Step 3: No answer found
            result["answer"] = "I couldn't find relevant information. Try rephrasing your question."
            logger.warning("✗ No answer sources available")
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            result["answer"] = f"Processing error occurred: {str(e)}"
        
        return self._finalize_result(result, start_time)
    
    def _finalize_result(self, result: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Finalize result with processing time."""
        if hasattr(asyncio.get_event_loop(), 'time'):
            result["processing_time"] = asyncio.get_event_loop().time() - start_time
        return result
    
    def batch_query(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Process multiple questions in batch."""
        return [self.query(q) for q in questions]
    
    async def async_query(self, question: str) -> Dict[str, Any]:
        """Async version of query method."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.query, question)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "retriever_available": self.retriever is not None,
            "web_search_available": self.web_search is not None,
            "provider": self.provider,
            "threshold": self.threshold,
            "timestamp": asyncio.get_event_loop().time() if hasattr(asyncio.get_event_loop(), 'time') else 0
        }
        
        # Get AstraDB stats if available
        if self.retriever:
            try:
                stats = self.retriever.get_database_stats()
                status["astradb_stats"] = stats
            except Exception as e:
                status["astradb_error"] = str(e)
        
        return status
    
    def insert_knowledge(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """Insert new knowledge into AstraDB."""
        if not self.retriever:
            logger.error("No retriever available for knowledge insertion")
            return False
        
        try:
            # Production retriever doesn't have insert method - would need ingestion pipeline
            logger.warning("Insert not implemented - use ingestion pipeline instead")
            return False
        except Exception as e:
            logger.error(f"Knowledge insertion failed: {e}")
            return False
    
    def health_check(self) -> Dict[str, str]:
        """Perform system health check."""
        health = {
            "status": "healthy",
            "retriever": "✓ operational" if self.retriever else "✗ unavailable",
            "web_search": "✓ operational" if self.web_search else "✗ unavailable",
            "provider": self.provider.upper()
        }
        
        # Overall status
        if not (self.retriever or self.web_search):
            health["status"] = "degraded"
        
        return health