"""
Enhanced Web Search with Multiple APIs - Under 120 lines
Supports Serper, Wikipedia, and DuckDuckGo for better real-time results
"""

import os
import logging
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    title: str
    snippet: str
    url: str = ""
    source: str = "web"

class EnhancedWebSearch:
    """Production web search with multiple APIs for real-time results"""
    
    def __init__(self, provider: str = "groq"):
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.provider = provider
        
        try:
            self.groq = Groq(api_key=self.groq_key) if Groq and self.groq_key else None
        except:
            self.groq = None
    
    def search_serper(self, query: str) -> List[SearchResult]:
        """Search using Serper API for real-time results"""
        if not self.serper_key:
            return []
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.serper_key, "Content-Type": "application/json"},
                json={"q": query, "num": 3}, timeout=8
            )
            if response.status_code == 200:
                return [SearchResult(item.get("title", ""), item.get("snippet", ""), 
                                   item.get("link", ""), "serper") 
                        for item in response.json().get("organic", [])[:2]]
        except Exception as e:
            logger.error(f"Serper failed: {e}")
        return []
    
    def search_all_sources(self, query: str) -> List[SearchResult]:
        """Search multiple sources: Serper, Wikipedia, DuckDuckGo"""
        results = []
        
        # Serper API
        results.extend(self.search_serper(query))
        
        # Wikipedia API
        if len(results) < 2:
            try:
                resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}", timeout=5)
                if resp.status_code == 200 and resp.json().get("extract"):
                    data = resp.json()
                    results.append(SearchResult(data.get("title", query), data["extract"][:200], 
                                              data.get("content_urls", {}).get("desktop", {}).get("page", ""), "wikipedia"))
            except:
                pass
        
        # DuckDuckGo fallback
        if len(results) < 2:
            try:
                resp = requests.get("https://api.duckduckgo.com/", 
                                  params={"q": f"{query} 2024 latest", "format": "json"}, timeout=5)
                data = resp.json()
                if data.get("Abstract"):
                    results.append(SearchResult(data.get("Heading", query), data["Abstract"], 
                                               data.get("AbstractURL", ""), "duckduckgo"))
            except:
                pass
        
        return results[:3]
    
    def search_and_summarize(self, query: str) -> str:
        """Main search with Groq summarization"""
        results = self.search_all_sources(query)
        if not results:
            return "I couldn't find current information. Please try rephrasing."
        
        if not self.groq:
            answer = " ".join([r.snippet for r in results[:2]])[:200]
        else:
            try:
                context = "\n".join([f"{r.source}: {r.snippet[:100]}" for r in results])
                response = self.groq.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": f"Answer '{query}' using: {context}. Be concise."}],
                    max_tokens=100, temperature=0.1
                )
                answer = response.choices[0].message.content.strip()
            except:
                answer = " ".join([r.snippet for r in results[:2]])[:200]
        
        sources = ", ".join(set([r.source for r in results]))
        return f"{answer}\n\n*Sources: {sources}*"
