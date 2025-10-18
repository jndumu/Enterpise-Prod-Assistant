"""
Unit Tests for Production RAG Application
"""

import unittest
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'app'))

class TestModeration(unittest.TestCase):
    def test_moderation_import(self):
        from src.app.core.moderation import moderate_user_input
        is_safe, msg = moderate_user_input("Hello")
        self.assertTrue(is_safe)

class TestWebSearch(unittest.TestCase):
    def test_search_import(self):
        from src.app.services.enhanced_web_search import EnhancedWebSearch
        search = EnhancedWebSearch()
        self.assertIsNotNone(search)

if __name__ == '__main__':
    unittest.main()
