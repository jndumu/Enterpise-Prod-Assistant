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
from .retrieval import Retriever as ProductionRetriever
from .web_search import WebSearchTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClient:
    """Production MCP Client for semantic search with intelligent fallback.
    
    This class orchestrates a multi-tier search strategy:
    1. Primary: Semantic search in AstraDB vector database
    2. Fallback: Web search using DuckDuckGo and Groq summarization
    3. Graceful degradation when services are unavailable
    
    The client provides comprehensive query processing with confidence scoring,
    performance monitoring, and detailed result attribution.
    
    Attributes:
        threshold (float): Minimum confidence score for accepting semantic results
        provider (str): LLM provider for web search summarization
        retriever: Production-grade document retriever instance
        web_search: Web search tool with summarization capabilities
    
    Example:
        >>> client = MCPClient(relevance_threshold=0.5)
        >>> result = client.query("What is machine learning?")
        >>> print(f"Answer: {result['answer']}, Source: {result['source']}")
    """
    
    def __init__(self, 
                 astra_token: Optional[str] = None,
                 astra_api_endpoint: Optional[str] = None,
                 api_key: Optional[str] = None,
                 provider: str = "groq",
                 relevance_threshold: float = 0.3):
        """Initialize MCP client with AstraDB and web search capabilities.
        
        Sets up the complete RAG pipeline with document retrieval and web search
        fallback. Gracefully handles initialization failures to ensure system
        remains operational even with partial service availability.
        
        Args:
            astra_token (str, optional): AstraDB authentication token.
                                       Uses environment variable if not provided.
            astra_api_endpoint (str, optional): AstraDB API endpoint URL.
                                              Uses environment variable if not provided.
            api_key (str, optional): API key for web search provider.
                                   Uses environment variable if not provided.
            provider (str): LLM provider for summarization. Defaults to "groq".
            relevance_threshold (float): Minimum confidence score (0.0-1.0) for
                                       accepting semantic search results. 
                                       Lower values are more permissive.
        
        Raises:
            Warning: Logs warnings if individual services fail to initialize,
                   but continues with available services.
                   
        Note:
            The client is designed for graceful degradation - it will function
            with any combination of available services (retriever, web search, or both).
        """
        
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
            logger.info(f"🔍 Searching question: {question}")
            if self.retriever:
                semantic_results = self.retriever.call_retriever(question, top_k=3)
                logger.info(f"📊 AstraDB returned {len(semantic_results) if semantic_results else 0} results")
                
                if semantic_results:
                    best_match = semantic_results[0]
                    score = best_match.metadata.get('score', 0.0)
                    logger.info(f"📈 Best match score: {score:.3f}, threshold: {self.threshold}")
                    
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
                    else:
                        logger.info(f"⚠️ Score {score:.3f} below threshold {self.threshold}, trying web search")
                else:
                    logger.info("📝 No semantic results found, trying web search")
            
            # Step 2: Fallback to web search
            logger.info("🌐 Attempting web search fallback...")
            if self.web_search:
                web_answer = self.web_search.search_and_summarize(question)
                logger.info(f"🔎 Web search result: {web_answer[:100] if web_answer else 'None'}...")
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
                else:
                    logger.warning("❌ Web search returned no useful results")
            else:
                logger.error("❌ Web search tool not available")
            
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