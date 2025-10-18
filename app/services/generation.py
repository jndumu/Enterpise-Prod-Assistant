# Response Generation Service - Under 50 lines
import logging
from typing import Dict, Any, Optional
from groq import Groq
import os

logger = logging.getLogger(__name__)

class GenerationService:
    def __init__(self, model: str = "llama-3.1-8b-instant", provider: str = "groq"):
        self.model = model
        self.provider = provider
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY')) if provider == "groq" else None
    
    def generate_response(self, query: str, context: str = "", conversation_history: str = "") -> Dict[str, Any]:
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
