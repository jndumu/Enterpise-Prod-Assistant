"""
Content Moderation and Guardrails - Under 120 lines
Prevents profanity and inappropriate content usage
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModerationResult:
    is_safe: bool
    flagged_content: List[str]
    reason: str
    confidence: float

class ContentModerator:
    """Production content moderation with guardrails"""
    
    def __init__(self):
        self.patterns = {
            'profanity': [r'\b(damn|hell|shit|fuck|bitch|ass)\b', r'\b(idiot|stupid|dumb)\b'],
            'harmful': [r'(how to (?:hack|break|steal|harm))', r'(make (?:bomb|weapon|drug))'],
            'inappropriate': [r'(sexual|porn|explicit)', r'(violence|gore)', r'(racist|discrimination)']
        }
    
    def check_patterns(self, text: str, category: str) -> List[str]:
        """Check text against pattern category"""
        flagged = []
        for pattern in self.patterns.get(category, []):
            matches = re.findall(pattern, text.lower(), re.IGNORECASE)
            flagged.extend(matches)
        return flagged
    
    def moderate_content(self, text: str, user_id: Optional[str] = None) -> ModerationResult:
        """Main moderation function"""
        if not text or not text.strip():
            return ModerationResult(True, [], "Empty content", 1.0)
        
        all_flagged, reasons = [], []
        for category in self.patterns.keys():
            flagged = self.check_patterns(text, category)
            if flagged:
                all_flagged.extend(flagged)
                reasons.append(category)
        
        is_safe = len(all_flagged) == 0
        reason = ", ".join(reasons) if reasons else "approved"
        
        if not is_safe:
            logger.warning(f"Moderation flag: {reason} - User: {user_id or 'anon'}")
        
        return ModerationResult(is_safe, list(set(all_flagged)), reason, 1.0 if is_safe else 0.7)
    
    def get_response(self, reason: str) -> str:
        """Get response for flagged content"""
        responses = {
            "profanity": "Please use appropriate language.",
            "harmful": "I cannot assist with harmful activities.",
            "inappropriate": "Please ask about appropriate topics."
        }
        return responses.get(reason.split(", ")[0], "I cannot assist with this request.")

# Global functions
moderator = ContentModerator()

def moderate_user_input(text: str, user_id: str = None) -> Tuple[bool, str]:
    """Quick moderation check"""
    result = moderator.moderate_content(text, user_id)
    return result.is_safe, "" if result.is_safe else moderator.get_response(result.reason)
