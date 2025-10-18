"""
Ultra-compact DuckDuckGo web search with Groq.
"""

import os
import logging
import requests
from typing import List, Optional
from dataclasses import dataclass

try:
    from groq import Groq
except ImportError:
    Groq = None

logger = logging.getLogger(__name__)

@dataclass
class WebSearchResult:
    title: str
    snippet: str
    url: str = ""

class WebSearchTool:
    """Ultra-compact web search using DuckDuckGo."""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "groq"):
        self.groq = Groq(api_key=api_key or os.getenv("GROQ_API_KEY")) if Groq else None
    
    def search_duckduckgo(self, query: str) -> List[WebSearchResult]:
        """Search DuckDuckGo free API."""
        try:
            response = requests.get("https://api.duckduckgo.com/", 
                                  params={'q': query, 'format': 'json'}, timeout=8)
            data = response.json()
            
            results = []
            if data.get('Abstract'):
                results.append(WebSearchResult(
                    title=data.get('Heading', query),
                    snippet=data['Abstract'],
                    url=data.get('AbstractURL', '')
                ))
            
            for topic in data.get('RelatedTopics', [])[:2]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append(WebSearchResult(
                        title=topic['Text'][:60] + '...',
                        snippet=topic['Text'],
                        url=topic.get('FirstURL', '')
                    ))
            
            return results or [WebSearchResult(
                title=f"About {query}",
                snippet=f"Information about {query} and related concepts."
            )]
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return [WebSearchResult(
                title=f"About {query}",
                snippet=f"General information about {query}."
            )]
    
    def summarize_with_groq(self, query: str, results: List[WebSearchResult]) -> str:
        """Summarize with Groq."""
        if not self.groq:
            return " ".join([r.snippet for r in results[:2]])[:200]
        
        try:
            # Simple inline prompt to avoid import issues
            context = "\\n".join([f"{r.title}: {r.snippet[:150]}" for r in results[:2]])
            prompt = f"Answer '{query}' using:\\n{context}\\nBe factual, under 100 words:"
            
            response = self.groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Groq failed: {e}")
            return " ".join([r.snippet for r in results[:2]])[:200]
    
    def search_and_summarize(self, query: str) -> str:
        """Search and summarize."""
        results = self.search_duckduckgo(query)
        return self.summarize_with_groq(query, results)