"""
Production Query Optimizer - Under 100 lines
Enhances query processing with semantic expansion and ranking optimization
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QueryContext:
    original: str
    expanded: str
    keywords: List[str]
    intent: str
    confidence: float

class QueryOptimizer:
    """Production query optimization and enhancement"""
    
    def __init__(self, groq_client=None):
        self.groq_client = groq_client
        self.intent_patterns = {
            'definition': [r'\bwhat is\b', r'\bdefine\b', r'\bmeans?\b', r'\bmeaning of\b'],
            'howto': [r'\bhow to\b', r'\bhow do\b', r'\bsteps to\b', r'\bprocess of\b'],
            'comparison': [r'\bvs\b', r'\bversus\b', r'\bcompare\b', r'\bdifference\b'],
            'example': [r'\bexample\b', r'\bfor instance\b', r'\bsuch as\b', r'\blike\b'],
            'troubleshoot': [r'\berror\b', r'\bproblem\b', r'\bissue\b', r'\bfailed?\b']
        }
        self.synonyms = {
            'ml': ['machine learning', 'artificial intelligence', 'AI'],
            'python': ['programming', 'coding', 'development'],
            'data': ['information', 'dataset', 'records'],
            'model': ['algorithm', 'system', 'framework']
        }
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract key terms from query"""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'to', 'are', 'as', 'of', 'in', 'for', 'with'}
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return list(set(keywords))
    
    def detect_intent(self, query: str) -> str:
        """Detect query intent"""
        query_lower = query.lower()
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        return 'general'
    
    def expand_with_synonyms(self, query: str) -> str:
        """Expand query with synonyms"""
        expanded = query
        query_lower = query.lower()
        
        for term, synonyms in self.synonyms.items():
            if term in query_lower:
                synonym_text = f" ({' OR '.join(synonyms)})"
                expanded = expanded.replace(term, f"{term}{synonym_text}", 1)
        
        return expanded
    
    def optimize_query(self, query: str) -> QueryContext:
        """Main query optimization"""
        keywords = self.extract_keywords(query)
        intent = self.detect_intent(query)
        expanded = self.expand_with_synonyms(query)
        
        # Calculate confidence based on query clarity
        confidence = min(0.9, 0.5 + len(keywords) * 0.1)
        
        return QueryContext(
            original=query,
            expanded=expanded,
            keywords=keywords,
            intent=intent,
            confidence=confidence
        )
    
    def rerank_results(self, results: List[Dict[str, Any]], context: QueryContext) -> List[Dict[str, Any]]:
        """Re-rank results based on query context"""
        if not results:
            return results
        
        for result in results:
            content = result.get('content', '').lower()
            score_boost = 0
            
            # Boost score for keyword matches
            for keyword in context.keywords:
                if keyword in content:
                    score_boost += 0.1
            
            # Boost based on intent matching
            if context.intent == 'definition' and any(word in content for word in ['is', 'means', 'defined']):
                score_boost += 0.15
            elif context.intent == 'howto' and any(word in content for word in ['step', 'process', 'method']):
                score_boost += 0.15
            
            # Apply score boost
            original_score = result.get('score', 0.0)
            result['optimized_score'] = min(1.0, original_score + score_boost)
            result['score_boost'] = score_boost
        
        # Sort by optimized score
        return sorted(results, key=lambda x: x.get('optimized_score', 0), reverse=True)

class OptimizedClient:
    """MCP client with query optimization"""
    
    def __init__(self, mcp_client):
        self.client = mcp_client
        self.optimizer = QueryOptimizer()
    
    def query(self, query: str, use_optimization: bool = True) -> Dict[str, Any]:
        """Query with optimization"""
        if not use_optimization:
            return self.client.query(query)
        
        # Optimize query
        context = self.optimizer.optimize_query(query)
        
        # Execute with optimized query
        if hasattr(self.client, 'call_retriever'):
            # Direct retriever access
            results = self.client.call_retriever(context.expanded, top_k=5)
            optimized_results = self.optimizer.rerank_results([
                {'content': r.page_content, 'score': r.metadata.get('score', 0.0), 'metadata': r.metadata}
                for r in results
            ], context)
            
            return {
                'query': query,
                'results': optimized_results,
                'optimization': {
                    'expanded_query': context.expanded,
                    'keywords': context.keywords,
                    'intent': context.intent,
                    'confidence': context.confidence
                },
                'success': True
            }
        else:
            # Standard client query
            result = self.client.query(context.expanded)
            result['optimization'] = {
                'expanded_query': context.expanded,
                'keywords': context.keywords,
                'intent': context.intent,
                'confidence': context.confidence
            }
            return result

def main():
    """Test query optimization"""
    optimizer = QueryOptimizer()
    
    # Test queries
    queries = [
        "What is machine learning?",
        "How to use Python for data science?",
        "Compare ML vs AI models"
    ]
    
    for query in queries:
        context = optimizer.optimize_query(query)
        print(f"Query: {query}")
        print(f"Intent: {context.intent}, Keywords: {context.keywords}")
        print(f"Expanded: {context.expanded}")
        print("-" * 50)

if __name__ == "__main__":
    main()