"""Document retrieval system for text-based AstraDB storage."""

import os
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from astrapy import DataAPIClient

logger = logging.getLogger(__name__)

@dataclass
class RetrievedDocument:
    """Represents a retrieved document chunk."""
    content: str
    metadata: Dict[str, Any]
    score: float = 0.0
    doc_id: str = ""

class DocumentRetriever:
    """Text-based document retriever for AstraDB stored content."""
    
    def __init__(self):
        """Initialize retriever with AstraDB connection."""
        load_dotenv()
        self._load_env_variables()
        self._connect_to_astradb()
        
    def _load_env_variables(self):
        """Load and validate environment variables."""
        required_vars = ["ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN"]
        missing_vars = [var for var in required_vars if os.getenv(var) is None]
        
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace")
        self.collection_name = os.getenv("COLLECTION_NAME", "semantic_data")
        
    def _connect_to_astradb(self):
        """Connect to AstraDB and get collection."""
        try:
            self.client = DataAPIClient(token=self.db_application_token)
            self.database = self.client.get_database_by_api_endpoint(self.db_api_endpoint)
            self.collection = self.database.get_collection(self.collection_name)
            logger.info(f"Connected to AstraDB collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to connect to AstraDB: {e}")
            raise
    
    def search_by_content(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """Search documents by content using text search."""
        try:
            # Get all documents and filter client-side (since AstraDB doesn't support $regex)
            all_docs = list(self.collection.find({}, limit=100))  # Get more docs for better search
            
            query_lower = query.lower()
            matched_docs = []
            
            for doc in all_docs:
                content = doc.get("content", "").lower()
                if query_lower in content:
                    # Simple relevance scoring based on query occurrences
                    score = content.count(query_lower)
                    
                    retrieved_doc = RetrievedDocument(
                        content=doc.get("content", ""),
                        metadata=doc.get("metadata", {}),
                        score=float(score),
                        doc_id=str(doc.get("_id", ""))
                    )
                    matched_docs.append(retrieved_doc)
            
            # Sort by relevance score and return top_k
            matched_docs.sort(key=lambda x: x.score, reverse=True)
            top_docs = matched_docs[:top_k]
            
            logger.info(f"Found {len(top_docs)} documents for query: {query[:50]}...")
            return top_docs
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def search_by_source(self, source_filename: str, top_k: int = 10) -> List[RetrievedDocument]:
        """Search documents by source filename."""
        try:
            search_filter = {
                "metadata.source": source_filename
            }
            
            results = list(self.collection.find(search_filter, limit=top_k))
            
            retrieved_docs = []
            for doc in results:
                retrieved_doc = RetrievedDocument(
                    content=doc.get("content", ""),
                    metadata=doc.get("metadata", {}),
                    score=1.0,
                    doc_id=str(doc.get("_id", ""))
                )
                retrieved_docs.append(retrieved_doc)
            
            logger.info(f"Found {len(retrieved_docs)} documents from source: {source_filename}")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Source search failed: {e}")
            return []
    
    def search_similar_content(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """Enhanced search using multiple keywords."""
        try:
            # Split query into keywords for better matching
            keywords = [word.strip().lower() for word in query.split() if len(word.strip()) > 3]
            
            if not keywords:
                return self.search_by_content(query, top_k)
            
            # Get all documents and score based on keyword matches
            all_docs = list(self.collection.find({}, limit=100))
            
            scored_docs = []
            for doc in all_docs:
                content_lower = doc.get("content", "").lower()
                score = sum(1 for keyword in keywords if keyword in content_lower)
                
                if score > 0:  # Only include docs that match at least one keyword
                    retrieved_doc = RetrievedDocument(
                        content=doc.get("content", ""),
                        metadata=doc.get("metadata", {}),
                        score=score / len(keywords),  # Normalize score
                        doc_id=str(doc.get("_id", ""))
                    )
                    scored_docs.append(retrieved_doc)
            
            # Sort by score and return top_k
            scored_docs.sort(key=lambda x: x.score, reverse=True)
            top_docs = scored_docs[:top_k]
            
            logger.info(f"Found {len(top_docs)} relevant documents for query: {query[:50]}...")
            return top_docs
            
        except Exception as e:
            logger.error(f"Similar content search failed: {e}")
            return self.search_by_content(query, top_k)  # Fallback
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about stored documents."""
        try:
            total_docs = self.collection.count_documents({}, upper_bound=10000)
            
            # Get sources
            pipeline = [
                {"$group": {"_id": "$metadata.source", "count": {"$sum": 1}}}
            ]
            
            # Simplified approach - get some sample docs to see sources
            sample_docs = list(self.collection.find({}, limit=100))
            sources = {}
            
            for doc in sample_docs:
                source = doc.get("metadata", {}).get("source", "unknown")
                sources[source] = sources.get(source, 0) + 1
            
            return {
                "total_documents": total_docs,
                "sources": sources,
                "collection_name": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
    
    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """Retrieve and format context for a query."""
        docs = self.search_similar_content(query, top_k)
        
        if not docs:
            return "No relevant documents found."
        
        formatted_chunks = []
        for i, doc in enumerate(docs, 1):
            meta = doc.metadata
            formatted = (
                f"Document {i} (Score: {doc.score:.2f}):\n"
                f"Source: {meta.get('source', 'N/A')}\n"
                f"Chunk: {meta.get('chunk_index', 'N/A')}\n"
                f"Content:\n{doc.content.strip()}"
            )
            formatted_chunks.append(formatted)
        
        return "\n\n" + "="*50 + "\n\n".join(formatted_chunks)

class EnhancedRetriever(DocumentRetriever):
    """Enhanced retriever with additional features."""
    
    def __init__(self):
        super().__init__()
        self.enable_groq = os.getenv("GROQ_API_KEY") is not None
        
        if self.enable_groq:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                logger.info("Groq client initialized for enhanced retrieval")
            except ImportError:
                logger.warning("Groq not available, using basic retrieval")
                self.enable_groq = False
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        """Enhanced semantic search with query expansion."""
        if self.enable_groq:
            try:
                # Use Groq to expand the query
                expanded_query = self._expand_query(query)
                logger.info(f"Expanded query: {expanded_query[:100]}...")
                return self.search_similar_content(expanded_query, top_k)
            except Exception as e:
                logger.warning(f"Groq expansion failed: {e}, falling back to basic search")
        
        return self.search_similar_content(query, top_k)
    
    def _expand_query(self, query: str) -> str:
        """Expand query using Groq for better matching."""
        try:
            prompt = f"""
            Expand this search query with related terms and synonyms to improve document retrieval.
            Original query: {query}
            
            Provide expanded keywords and phrases (keep it concise):
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                max_tokens=150,
                temperature=0.3
            )
            
            expanded = response.choices[0].message.content.strip()
            return f"{query} {expanded}"
            
        except Exception as e:
            logger.error(f"Query expansion failed: {e}")
            return query

def main():
    """Test the retrieval system."""
    print("🔍 Testing Document Retrieval System...")
    
    try:
        # Initialize retriever
        retriever = EnhancedRetriever()
        
        # Get stats
        stats = retriever.get_document_stats()
        print(f"\n📊 Database Stats:")
        print(f"   Total documents: {stats.get('total_documents', 0)}")
        print(f"   Sources: {stats.get('sources', {})}")
        
        # Test queries
        test_queries = [
            "retrieval augmented generation",
            "knowledge intensive tasks",
            "neural language models"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            docs = retriever.semantic_search(query, top_k=3)
            
            if docs:
                print(f"   Found {len(docs)} relevant documents:")
                for i, doc in enumerate(docs, 1):
                    print(f"   {i}. Score: {doc.score:.2f} | Source: {doc.metadata.get('source', 'N/A')}")
                    print(f"      Content: {doc.content[:100]}...")
            else:
                print("   No relevant documents found")
        
        print(f"\n✅ Retrieval system working successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()