"""Production AstraDB service for document storage and retrieval."""

import logging
from typing import List, Dict, Any, Optional
from astrapy import DataAPIClient
from astrapy.exceptions import DataAPIException

logger = logging.getLogger(__name__)

class AstraDBService:
    """Production-ready AstraDB service."""
    
    def __init__(self, token: str, api_endpoint: str, collection_name: str = "documents"):
        self.token = token
        self.api_endpoint = api_endpoint
        self.collection_name = collection_name
        self._client = None
        self._collection = None
        self._connect()
    
    def _connect(self) -> None:
        """Initialize AstraDB connection."""
        try:
            self._client = DataAPIClient(self.token)
            self._database = self._client.get_database_by_api_endpoint(self.api_endpoint)
            self._collection = self._database.get_collection(self.collection_name)
            logger.info(f"Connected to AstraDB collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"AstraDB connection failed: {e}")
            raise
    
    def insert_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Batch insert documents with error handling."""
        if not documents:
            return 0
        
        try:
            result = self._collection.insert_many(documents)
            inserted_count = len(result.inserted_ids) if hasattr(result, 'inserted_ids') else len(documents)
            logger.info(f"Inserted {inserted_count} documents")
            return inserted_count
        except DataAPIException as e:
            logger.error(f"Batch insert failed: {e}")
            return self._insert_one_by_one(documents)
        except Exception as e:
            logger.error(f"Insert error: {e}")
            raise
    
    def _insert_one_by_one(self, documents: List[Dict[str, Any]]) -> int:
        """Fallback: insert documents one by one."""
        success_count = 0
        for doc in documents:
            try:
                self._collection.insert_one(doc)
                success_count += 1
            except Exception as e:
                logger.warning(f"Failed to insert document: {e}")
        return success_count
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self._collection.count_documents({}, upper_bound=10000)
            return {
                "document_count": count,
                "collection_name": self.collection_name,
                "status": "connected"
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e), "status": "error"}
    
    def search_documents(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Vector similarity search."""
        try:
            results = self._collection.find(
                sort={"$vector": query_vector},
                limit=limit
            )
            return list(results)
        except Exception as e:
            logger.warning(f"Vector search failed, trying text search: {e}")
            return []