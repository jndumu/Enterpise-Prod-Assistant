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
    query: str
    response: str
    source: str
    confidence: float
    timestamp: datetime

class ConversationMemory:
    """Production conversation memory with context management"""
    
    def __init__(self, max_turns: int = 5, max_age_hours: int = 24):
        self.max_turns = max_turns
        self.max_age = timedelta(hours=max_age_hours)
        self.conversations: Dict[str, List[Turn]] = {}
    
    def add_turn(self, session_id: str, query: str, response: str, source: str, confidence: float):
        """Add conversation turn"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        turn = Turn(query, response, source, confidence, datetime.now())
        self.conversations[session_id].append(turn)
        
        # Keep only recent turns
        if len(self.conversations[session_id]) > self.max_turns:
            self.conversations[session_id] = self.conversations[session_id][-self.max_turns:]
    
    def get_context(self, session_id: str, num_turns: int = 2) -> str:
        """Get conversation context"""
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