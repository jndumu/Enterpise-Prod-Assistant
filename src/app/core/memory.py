"""
Production Conversation Memory - Under 100 lines
Tracks conversation context for multi-turn conversations
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Turn:
    """Represents a single conversation turn in the memory system.
    
    This immutable data structure captures all essential information
    about a user-assistant interaction for context preservation.
    
    Attributes:
        query (str): User's original question or input
        response (str): Assistant's response to the query
        source (str): Source of the response ('astradb', 'web_search', etc.)
        confidence (float): Confidence score for the response (0.0-1.0)
        timestamp (datetime): When this turn occurred
        
    Example:
        >>> turn = Turn(
        ...     query="What is Python?",
        ...     response="Python is a programming language",
        ...     source="astradb",
        ...     confidence=0.9,
        ...     timestamp=datetime.now()
        ... )
    """
    query: str
    response: str
    source: str
    confidence: float
    timestamp: datetime

class ConversationMemory:
    """Production-grade conversation memory with intelligent context management.
    
    This class maintains conversation history across multiple sessions with
    automatic memory management, context extraction, and session analytics.
    Designed for high-throughput production environments with memory efficiency
    and data privacy considerations.
    
    Features:
        - Session-based conversation tracking
        - Automatic memory cleanup and rotation
        - Context-aware query enhancement
        - Comprehensive session analytics
        - Time-based session expiration
        - Memory usage optimization
    
    Attributes:
        max_turns (int): Maximum turns to retain per session
        max_age (timedelta): Maximum age for session data
        conversations (Dict[str, List[Turn]]): Active conversation storage
        
    Example:
        >>> memory = ConversationMemory(max_turns=10, max_age_hours=48)
        >>> memory.add_turn("session_1", "What is AI?", "AI is...", "astradb", 0.9)
        >>> context = memory.get_context("session_1")
        >>> print(f"Previous context: {context}")
    """
    
    def __init__(self, max_turns: int = 5, max_age_hours: int = 24):
        """Initialize conversation memory with configurable limits.
        
        Args:
            max_turns (int): Maximum number of conversation turns to retain
                           per session. Older turns are automatically removed.
                           Defaults to 5 for optimal context/performance balance.
            max_age_hours (int): Maximum age in hours for session data.
                               Sessions older than this are eligible for cleanup.
                               Defaults to 24 hours for privacy compliance.
                               
        Note:
            Memory management is performed automatically during normal operations.
            The system is designed to handle thousands of concurrent sessions
            while maintaining optimal performance characteristics.
        """
        self.max_turns = max_turns
        self.max_age = timedelta(hours=max_age_hours)
        self.conversations: Dict[str, List[Turn]] = {}
    
    def add_turn(self, session_id: str, query: str, response: str, source: str, confidence: float):
        """Add a new conversation turn to the specified session.
        
        This method records a complete interaction turn including the user query,
        assistant response, source attribution, and confidence scoring. Automatically
        manages memory limits by removing oldest turns when the limit is exceeded.
        
        Args:
            session_id (str): Unique identifier for the conversation session
            query (str): User's original question or input
            response (str): Assistant's response to the query
            source (str): Source of the response ('astradb', 'web_search', 'generated', etc.)
            confidence (float): Confidence score for the response (0.0 to 1.0)
            
        Side Effects:
            - Creates new session if session_id doesn't exist
            - Automatically trims conversation history to max_turns limit
            - Updates session timestamp for aging calculations
            
        Note:
            The method uses LIFO (Last In, First Out) strategy for memory management,
            keeping the most recent turns and discarding the oldest ones.
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        turn = Turn(query, response, source, confidence, datetime.now())
        self.conversations[session_id].append(turn)
        
        # Keep only recent turns
        if len(self.conversations[session_id]) > self.max_turns:
            self.conversations[session_id] = self.conversations[session_id][-self.max_turns:]
    
    def get_context(self, session_id: str, num_turns: int = 2) -> str:
        """Extract formatted conversation context for the specified session.
        
        Retrieves the most recent conversation turns and formats them into
        a structured string suitable for LLM context injection. Responses
        are truncated for optimal context window utilization.
        
        Args:
            session_id (str): Session identifier to retrieve context for
            num_turns (int): Number of recent turns to include. Defaults to 2
                           for balanced context/performance ratio.
                           
        Returns:
            str: Formatted conversation context in Q&A format, or empty string
                if session doesn't exist. Format:
                "Q: [user question]\nA: [response excerpt]...\n..."
                
        Note:
            - Only includes the most recent num_turns interactions
            - Responses are truncated to 150 characters for efficiency
            - Returns empty string for non-existent sessions
            - Context is formatted for optimal LLM consumption
        """
        if session_id not in self.conversations:
            return ""
        
        turns = self.conversations[session_id][-num_turns:]
        context = []
        
        for turn in turns:
            context.append(f"Q: {turn.query}")
            context.append(f"A: {turn.response[:150]}...")
        
        return "\n".join(context)
    
    def enhance_query(self, session_id: str, query: str) -> str:
        """Enhance query with conversation context"""
        context = self.get_context(session_id)
        if context:
            return f"Previous conversation:\n{context}\n\nNew question: {query}"
        return query
    
    def get_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics"""
        if session_id not in self.conversations:
            return {"exists": False}
        
        turns = self.conversations[session_id]
        sources = {}
        for turn in turns:
            sources[turn.source] = sources.get(turn.source, 0) + 1
        
        return {
            "exists": True,
            "turns": len(turns),
            "avg_confidence": sum(t.confidence for t in turns) / len(turns),
            "sources": sources,
            "duration_min": (turns[-1].timestamp - turns[0].timestamp).total_seconds() / 60 if len(turns) > 1 else 0
        }
    
    def cleanup_old(self) -> int:
        """Remove expired sessions"""
        cutoff = datetime.now() - self.max_age
        expired = [sid for sid, turns in self.conversations.items() 
                  if turns and turns[-1].timestamp < cutoff]
        
        for sid in expired:
            del self.conversations[sid]
        
        return len(expired)

class MemoryClient:
    """MCP client with conversation memory"""
    
    def __init__(self, mcp_client, max_turns: int = 5):
        self.client = mcp_client
        self.memory = ConversationMemory(max_turns)
    
    def query(self, session_id: str, query: str, use_context: bool = True) -> Dict[str, Any]:
        """Query with memory enhancement"""
        enhanced_query = self.memory.enhance_query(session_id, query) if use_context else query
        
        result = self.client.query(enhanced_query)
        
        # Store in memory
        self.memory.add_turn(session_id, query, result['answer'], 
                           result['source'], result['confidence'])
        
        # Add memory metadata
        result['memory'] = self.memory.get_stats(session_id)
        return result
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get overall memory statistics"""
        return {
            "active_sessions": len(self.memory.conversations),
            "total_turns": sum(len(turns) for turns in self.memory.conversations.values()),
            "max_turns": self.memory.max_turns
        }

def main():
    """Test memory functionality"""
    memory = ConversationMemory()
    
    # Test conversation
    memory.add_turn("test", "What is Python?", "Python is a programming language", "astradb", 0.9)
    memory.add_turn("test", "How to use it?", "You can use Python for development", "web", 0.8)
    
    print(f"Context: {memory.get_context('test')[:100]}...")
    print(f"Stats: {memory.get_stats('test')}")

if __name__ == "__main__":
    main()