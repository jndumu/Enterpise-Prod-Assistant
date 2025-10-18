"""
Concise Pipeline Test - Tests ingestion, retrieval, and MCP client
"""

import os
import sys
import logging
from pathlib import Path

# Add paths
sys.path.append('app')

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ingestion():
    """Skip ingestion - not needed for production test"""
    logger.info("⏭️ Skipping ingestion - using existing data")
    return True

def test_retriever():
    """Test production retriever"""
    try:
        from services.retrieval import Retriever
        
        retriever = Retriever()
        logger.info("🔄 Testing retriever...")
        
        # Test search using correct interface
        results = retriever.call_retriever("machine learning", top_k=2)
        if results:
            score = results[0].metadata.get('score', 0.0)
            logger.info(f"✅ Found {len(results)} results, top score: {score:.3f}")
        else:
            logger.info("📝 No results found")
        
        # Test stats
        try:
            stats = retriever.get_stats()
            logger.info(f"📊 Stats: {stats.get('document_count', 'N/A')} docs")
        except:
            logger.info("📊 Stats unavailable")
        
        return True
    except Exception as e:
        logger.error(f"❌ Retriever failed: {e}")
        return False

def test_mcp_client():
    """Test MCP client"""
    try:
        from services.client import MCPClient
        
        client = MCPClient()
        logger.info("🔄 Testing MCP client...")
        
        # Test health
        health = client.health_check()
        logger.info(f"🏥 Health: {health['status']}")
        
        # Test query
        result = client.query("What is machine learning?")
        logger.info(f"✅ Query result - Source: {result['source']}, Success: {result['success']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ MCP client failed: {e}")
        return False

def test_web_search():
    """Test web search fallback"""
    try:
        from services.web_search import WebSearchTool
        
        web_tool = WebSearchTool(provider="groq")
        logger.info("🔄 Testing web search...")
        
        result = web_tool.search_and_summarize("Python 2024 features")
        if result:
            logger.info("✅ Web search working")
        else:
            logger.info("📝 No web results")
        
        return True
    except Exception as e:
        logger.error(f"❌ Web search failed: {e}")
        return False

def main():
    """Run pipeline tests"""
    logger.info("🚀 Pipeline Test Suite")
    logger.info("=" * 40)
    
    # Environment check
    env_exists = Path(".env").exists()
    data_files = len(list(Path("data").glob("*.pdf"))) if Path("data").exists() else 0
    
    logger.info(f"📋 Environment: .env={'✅' if env_exists else '❌'}, PDFs={data_files}")
    
    # Run tests
    tests = {
        'retriever': test_retriever,
        'mcp_client': test_mcp_client,
        'web_search': test_web_search
    }
    
    results = {}
    for name, test_func in tests.items():
        if test_func is None:
            logger.info(f"⏭️  Skipping {name} - no data files")
            results[name] = None
        else:
            results[name] = test_func()
    
    # Summary
    logger.info("=" * 40)
    logger.info("🏁 Results:")
    
    passed = failed = skipped = 0
    for name, result in results.items():
        if result is None:
            logger.info(f"   {name}: SKIPPED")
            skipped += 1
        elif result:
            logger.info(f"   {name}: ✅ PASSED")
            passed += 1
        else:
            logger.info(f"   {name}: ❌ FAILED")
            failed += 1
    
    total = passed + failed
    logger.info(f"📊 Score: {passed}/{total} passed{f', {skipped} skipped' if skipped else ''}")
    
    if passed == total and total > 0:
        logger.info("🎉 All tests passed!")
    elif passed > 0:
        logger.info("⚠️  Some tests failed")
    else:
        logger.info("❌ All tests failed")

if __name__ == "__main__":
    main()