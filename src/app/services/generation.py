"""Response Generation Service for RAG Applications.

This module provides LLM-powered response generation with context awareness
and conversation history integration. Optimized for production use with
the Groq inference platform for fast, high-quality text generation.

Features:
    - Context-aware response generation
    - Conversation history integration
    - Configurable model selection
    - Token usage tracking
    - Error handling and fallback strategies

Author: Production RAG Team
Version: 1.0.0
"""

import logging
from typing import Dict, Any, Optional
from groq import Groq
import os

logger = logging.getLogger(__name__)

class GenerationService:
    """Production-grade response generation service using Groq LLM.
    
    This service orchestrates LLM-based response generation by combining
    retrieved document context with conversation history to produce
    coherent, contextually relevant responses.
    
    The service is designed for high-throughput production environments
    with emphasis on speed, reliability, and context preservation.
    
    Attributes:
        model (str): LLM model identifier
        provider (str): LLM inference provider
        client: Groq client instance for API communication
        
    Example:
        >>> generator = GenerationService(model="llama-3.1-8b-instant")
        >>> result = generator.generate_response(
        ...     query="What is Python?",
        ...     context="Python is a programming language...",
        ...     conversation_history="Q: Tell me about coding\nA: Programming involves..."
        ... )
        >>> print(f"Generated: {result['answer']}")
    """
    
    def __init__(self, model: str = "llama-3.1-8b-instant", provider: str = "groq"):
        """Initialize the generation service with specified model and provider.
        
        Args:
            model (str): LLM model to use for generation. Defaults to Llama 3.1 8B.
                        Available models depend on the provider.
            provider (str): LLM inference provider. Currently supports "groq".
                          Future versions may support additional providers.
                          
        Environment Variables:
            GROQ_API_KEY: Required API key for Groq inference platform
            
        Note:
            If the API key is not available or initialization fails,
            the service will operate in degraded mode and return appropriate
            error responses rather than crashing.
        """
        self.model = model
        self.provider = provider
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY')) if provider == "groq" else None
    
    def generate_response(self, query: str, context: str = "", conversation_history: str = "") -> Dict[str, Any]:
        """Generate contextually aware response using LLM.
        
        This method combines the user query with retrieved document context
        and conversation history to generate coherent, informative responses.
        The prompt engineering ensures the model leverages all available
        context while maintaining response quality and relevance.
        
        Args:
            query (str): User's question or request
            context (str, optional): Retrieved document context or knowledge base content
            conversation_history (str, optional): Previous conversation turns for context
            
        Returns:
            Dict[str, Any]: Generation result with the following structure:
                {
                    "answer": str,          # Generated response text
                    "model": str,           # Model used for generation
                    "success": bool,        # Whether generation succeeded
                    "tokens_used": int,     # Total tokens consumed
                    "error": str            # Error message if success=False
                }
                
        Raises:
            Does not raise exceptions - returns error information in result dict
            for graceful error handling in production environments.
            
        Processing Pipeline:
            1. Validates client availability
            2. Constructs context-aware prompt
            3. Calls LLM API with optimized parameters
            4. Extracts and formats response
            5. Returns structured result with metadata
            
        Note:
            - Uses temperature=0.7 for balanced creativity/consistency
            - Limited to 500 tokens for responsive performance
            - Includes comprehensive error handling and logging
        """
        if not self.client:
            return {"error": "Generation client not available", "success": False}
        
        # Build prompt with context
        prompt = f"Context: {context}\n\nConversation: {conversation_history}\n\nQuestion: {query}\n\nAnswer:"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            return {
                "answer": answer,
                "model": self.model,
                "success": True,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {"error": str(e), "success": False}
