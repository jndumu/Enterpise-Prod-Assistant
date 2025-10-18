"""Production retriever following the sample pattern structure."""

import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from dataclasses import dataclass

try:
    from .document_retriever import EnhancedRetriever
except ImportError:
    from document_retriever import EnhancedRetriever

logger = logging.getLogger(__name__)

@dataclass
class Document:
    """Document class compatible with LangChain-style interfaces."""
    page_content: str
    metadata: Dict[str, Any]

class Retriever:
    """Production retriever following your sample code pattern."""
    
    def __init__(self):
        """Initialize retriever with configuration."""
        self._load_env_variables()
        self.retriever_instance = None
        self.document_retriever = None
        
    def _load_env_variables(self):
        """Load environment variables."""
        load_dotenv()
         
        required_vars = ["ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN"]
        missing_vars = [var for var in required_vars if os.getenv(var) is None]
        
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")

        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE", "default_keyspace")
        self.collection_name = os.getenv("COLLECTION_NAME", "semantic_data")
    
    def load_retriever(self):
        """Load and initialize the retriever."""
        if not self.document_retriever:
            self.document_retriever = EnhancedRetriever()
            logger.info("Document retriever loaded successfully.")
            
        return self.document_retriever
            
    def call_retriever(self, query: str, top_k: int = 5) -> List[Document]:
        """Main retriever interface following your sample pattern."""
        retriever = self.load_retriever()
        
        # Get documents using our custom retriever
        retrieved_docs = retriever.semantic_search(query, top_k=top_k)
        
        # Convert to LangChain-style Document objects
        documents = []
        for doc in retrieved_docs:
            document = Document(
                page_content=doc.content,
                metadata={
                    **doc.metadata,
                    "score": doc.score,
                    "doc_id": doc.doc_id
                }
            )
            documents.append(document)
        
        return documents
    
    def search_by_source(self, source_filename: str, top_k: int = 10) -> List[Document]:
        """Search documents from specific source."""
        retriever = self.load_retriever()
        retrieved_docs = retriever.search_by_source(source_filename, top_k)
        
        documents = []
        for doc in retrieved_docs:
            document = Document(
                page_content=doc.content,
                metadata={
                    **doc.metadata,
                    "score": doc.score,
                    "doc_id": doc.doc_id
                }
            )
            documents.append(document)
        
        return documents
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        retriever = self.load_retriever()
        return retriever.get_document_stats()

def _format_docs(docs: List[Document]) -> str:
    """Format documents for display (following your sample pattern)."""
    if not docs:
        return "No relevant documents found."
    
    formatted_chunks = []
    for d in docs:
        meta = d.metadata or {}
        formatted = (
            f"Source: {meta.get('source', 'N/A')}\n"
            f"Chunk: {meta.get('chunk_index', 'N/A')}\n"
            f"Score: {meta.get('score', 'N/A')}\n"
            f"Content:\n{d.page_content.strip()}"
        )
        formatted_chunks.append(formatted)
    
    return "\n\n---\n\n".join(formatted_chunks)

# Example usage following your pattern
if __name__ == '__main__':
    # Example queries for PDF content
    test_queries = [
        "What is retrieval augmented generation?",
        "How do neural language models work?",
        "What are knowledge-intensive NLP tasks?"
    ]
    
    retriever_obj = Retriever()
    
    # Get database stats first
    stats = retriever_obj.get_database_stats()
    print(f"📊 Database Stats: {stats}")
    
    for user_query in test_queries:
        print(f"\n🔍 Query: {user_query}")
        
        # Retrieve relevant documents
        retrieved_docs = retriever_obj.call_retriever(user_query, top_k=3)
        
        if retrieved_docs:
            # Format documents
            formatted_context = _format_docs(retrieved_docs)
            
            print(f"📄 Retrieved {len(retrieved_docs)} documents:")
            print(f"\n{formatted_context}")
            
            # Example response (in real scenario, this would come from your LLM)
            response = f"Based on the retrieved documents, I can provide information about {user_query.lower()}."
            
            print(f"\n🤖 Response: {response}")
            
            # You can add evaluation metrics here if needed
            # context_score = evaluate_context_precision(user_query, response, [formatted_context])
            # relevancy_score = evaluate_response_relevancy(user_query, response, [formatted_context])
            
        else:
            print("❌ No relevant documents found")
        
        print("\n" + "="*80)