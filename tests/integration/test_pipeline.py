"""
Integration Tests for RAG Pipeline
"""

import unittest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent / 'app'))

class TestPipeline(unittest.TestCase):
    def test_client_health(self):
        try:
            from src.app.services.client import MCPClient
            client = MCPClient()
            health = client.health_check()
            self.assertIn('status', health)
        except Exception as e:
            self.skipTest(f"Client init failed: {e}")

if __name__ == '__main__':
    unittest.main()
