"""
Prompt templates for Enterprise Production Assistant
Standardizes AI response formatting and context handling
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

class PromptTemplates:
    """Collection of prompt templates for consistent AI responses"""
    
    DOCUMENT_ANSWER_TEMPLATE = """
Based on the uploaded document, I found relevant information:

{answer}

Source: {filename} (Page {page})
Confidence: {confidence:.0%}
"""

    WEB_SEARCH_TEMPLATE = """
I couldn't find the answer in your uploaded documents, so I searched the web:

{answer}

Source: Web Search (DuckDuckGo)
Note: This information is from external sources and may not be related to your documents.
"""

    NO_ANSWER_TEMPLATE = """
I couldn't find relevant information for your question "{question}".

Suggestions:
• Upload relevant documents that might contain the answer
• Try rephrasing your question with different keywords  
• Check if your question is related to the content you've uploaded

Feel free to try a different question or upload additional documents.
"""

    ERROR_TEMPLATE = """
I encountered an error while processing your request:

Error: {error}

Please try again or contact support if the issue persists.
"""

    DOCUMENT_UPLOAD_SUCCESS = """
✅ Document uploaded successfully!

File: {filename}
Pages: {pages}
Text chunks: {chunks_count}

Your document is now ready for questions. Ask me anything about its content!
"""

    SYSTEM_STATUS_TEMPLATE = """
🔍 System Status:
• Document Retrieval: {retriever_status}
• Web Search: {web_status}  
• Search Provider: {provider}
• Total Documents: {doc_count}
• Active Since: {uptime}
"""

    @classmethod
    def format_response(cls, response_data: Dict[str, Any]) -> str:
        """Format a response using appropriate template"""
        
        if not response_data.get('success', False):
            return cls.ERROR_TEMPLATE.format(
                error=response_data.get('error', 'Unknown error')
            )
        
        source = response_data.get('source', 'none')
        
        if source == 'document':
            return cls.DOCUMENT_ANSWER_TEMPLATE.format(
                answer=response_data.get('answer', ''),
                filename=response_data.get('filename', 'Unknown'),
                page=response_data.get('metadata', {}).get('page', '?'),
                confidence=response_data.get('confidence', 0)
            )
        
        elif source == 'web':
            return cls.WEB_SEARCH_TEMPLATE.format(
                answer=response_data.get('answer', '')
            )
        
        else:
            return cls.NO_ANSWER_TEMPLATE.format(
                question=response_data.get('question', '')
            )
    
    @classmethod
    def format_upload_success(cls, upload_data: Dict[str, Any]) -> str:
        """Format successful upload response"""
        return cls.DOCUMENT_UPLOAD_SUCCESS.format(
            filename=upload_data.get('filename', 'Unknown'),
            pages=upload_data.get('pages', 0),
            chunks_count=upload_data.get('chunks_count', 0)
        )
    
    @classmethod
    def format_system_status(cls, status_data: Dict[str, Any]) -> str:
        """Format system status response"""
        return cls.SYSTEM_STATUS_TEMPLATE.format(
            retriever_status="✅ Available" if status_data.get('retriever_available') else "❌ Unavailable",
            web_status="✅ Available" if status_data.get('web_search_available') else "❌ Unavailable",
            provider=status_data.get('provider', 'Unknown'),
            doc_count=status_data.get('document_stats', {}).get('total_documents', 0),
            uptime=datetime.fromtimestamp(status_data.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M')
        )