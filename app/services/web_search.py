"""
Web search service for fallback queries
"""

import requests
from typing import Optional, Dict
from ..core.config import settings
from ..core.exceptions import SearchError

class WebSearchService:
    """Service for web search fallback"""
    
    def search_duckduckgo(self, query: str) -> Optional[Dict]:
        """Search using DuckDuckGo API"""
        try:
            response = requests.get(
                f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1",
                timeout=settings.SEARCH_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("Abstract"):
                return {
                    "answer": data["Abstract"],
                    "source": "web",
                    "confidence": 0.75
                }
            return None
            
        except Exception as e:
            raise SearchError(f"Web search failed: {str(e)}")
    
    def search(self, query: str) -> Optional[Dict]:
        """Main search method with fallback"""
        try:
            return self.search_duckduckgo(query)
        except SearchError:
            return None