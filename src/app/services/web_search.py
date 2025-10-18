"""
Ultra-compact DuckDuckGo web search with Groq.
"""

import os
import logging
import requests
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        try:
            groq_key = api_key or os.getenv("GROQ_API_KEY")
            self.groq = Groq(api_key=groq_key) if Groq and groq_key else None
        except Exception:
            self.groq = None
    
    def search_duckduckgo(self, query: str) -> List[WebSearchResult]:
        """Enhanced DuckDuckGo search with real-time focus."""
        try:
            # Try multiple search strategies for better real-time results
            search_queries = [
                f"{query} 2024 2025 latest current",  # Add temporal terms
                f"{query} recent news today",           # News focus
                query                                    # Original query
            ]
            
            all_results = []
            
            for search_query in search_queries:
                try:
                    response = requests.get("https://api.duckduckgo.com/", 
                                          params={'q': search_query, 'format': 'json'}, timeout=6)
                    data = response.json()
                    
                    # Process abstract
                    if data.get('Abstract'):
                        all_results.append(WebSearchResult(
                            title=data.get('Heading', query),
                            snippet=data['Abstract'],
                            url=data.get('AbstractURL', '')
                        ))
                    
                    # Process related topics with better filtering
                    for topic in data.get('RelatedTopics', []):
                        if isinstance(topic, dict) and 'Text' in topic:
                            text = topic['Text']
                            # Prioritize recent content
                            if any(term in text.lower() for term in ['2024', '2025', 'current', 'latest', 'recent', 'now']):
                                all_results.append(WebSearchResult(
                                    title=text[:60] + '...',
                                    snippet=text,
                                    url=topic.get('FirstURL', '')
                                ))
                    
                    # Break if we have good results
                    if len(all_results) >= 2:
                        break
                        
                except Exception:
                    continue
            
            # Try news-specific search if no good results
            if not all_results:
                try:
                    news_response = requests.get("https://api.duckduckgo.com/", 
                                               params={'q': f"news {query}", 'format': 'json'}, timeout=6)
                    news_data = news_response.json()
                    
                    if news_data.get('Abstract'):
                        all_results.append(WebSearchResult(
                            title=f"Recent: {query}",
                            snippet=news_data['Abstract'],
                            url=news_data.get('AbstractURL', '')
                        ))
                except Exception:
                    pass
            
            return all_results[:3] or [WebSearchResult(
                title=f"About {query}",
                snippet=f"Current information about {query}. Please note: Search results may have limited real-time data."
            )]
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return [WebSearchResult(
                title=f"About {query}",
                snippet=f"Unable to fetch current information about {query}. Please try rephrasing your question."
            )]
    
    def summarize_with_groq(self, query: str, results: List[WebSearchResult]) -> str:
        """Enhanced Groq summarization with real-time awareness."""
        if not self.groq:
            return " ".join([r.snippet for r in results[:2]])[:200]
        
        try:
            # Get current date for context
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Enhanced context with temporal awareness
            context = "\\n".join([f"{r.title}: {r.snippet[:150]}" for r in results[:2]])
            
            # Enhanced prompt for better real-time responses
            prompt = f"""Current date: {current_date}
            
Question: {query}
            
Web search results:
{context}
            
Provide a current, accurate answer based on the search results. If the results mention dates or recent events, prioritize the most recent information. Be factual and concise (under 100 words). If you cannot find current information, acknowledge this limitation.
            
Answer:"""
            
            response = self.groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides current, accurate information based on web search results. Always prioritize recent information and acknowledge when information might be outdated."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Groq failed: {e}")
            return " ".join([r.snippet for r in results[:2]])[:200]
    
    def search_alternative_apis(self, query: str) -> List[WebSearchResult]:
        """Try alternative search approaches for better real-time results."""
        results = []
        
        # Try Wikipedia API for current events
        try:
            wiki_response = requests.get(
                "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_"),
                timeout=5
            )
            if wiki_response.status_code == 200:
                wiki_data = wiki_response.json()
                if 'extract' in wiki_data:
                    results.append(WebSearchResult(
                        title=wiki_data.get('title', query),
                        snippet=wiki_data['extract'][:200],
                        url=wiki_data.get('content_urls', {}).get('desktop', {}).get('page', '')
                    ))
        except:
            pass
        
        # Try searching for news-specific terms
        news_terms = ['president', 'minister', 'election', 'current', 'latest', '2024', '2025']
        if any(term.lower() in query.lower() for term in news_terms):
            try:
                news_query = f"current {query} 2024 latest news"
                response = requests.get("https://api.duckduckgo.com/", 
                                      params={'q': news_query, 'format': 'json', 'no_html': '1'}, 
                                      timeout=6)
                data = response.json()
                
                if data.get('Abstract'):
                    results.append(WebSearchResult(
                        title=f"Latest: {query}",
                        snippet=data['Abstract'],
                        url=data.get('AbstractURL', '')
                    ))
            except:
                pass
        
        return results
    
    def search_and_summarize(self, query: str) -> str:
        """Enhanced search and summarize with multiple strategies."""
        # Try enhanced DuckDuckGo search first
        results = self.search_duckduckgo(query)
        
        # If no good results, try alternative methods
        if not results or len(results) < 2:
            alt_results = self.search_alternative_apis(query)
            results.extend(alt_results)
        
        # Deduplicate results
        unique_results = []
        seen_snippets = set()
        for result in results:
            if result.snippet not in seen_snippets:
                unique_results.append(result)
                seen_snippets.add(result.snippet)
        
        return self.summarize_with_groq(query, unique_results[:3])
