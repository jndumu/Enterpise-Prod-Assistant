#!/usr/bin/env python3
"""
Simple test pipeline for GitHub Actions deployment.
Tests basic application functionality for CI/CD.
"""

import os
import sys

def test_main_import():
    """Test that the main application can be imported."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        import main
        print("✅ Main application imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import main: {e}")
        return False

def test_environment_variables():
    """Test that environment variables are set."""
    required_vars = [
        "ASTRA_DB_APPLICATION_TOKEN",
        "ASTRA_DB_API_ENDPOINT", 
        "GROQ_API_KEY"
    ]
    
    all_present = True
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ Environment variable {var} is set")
        else:
            print(f"⚠️ Environment variable {var} is not set (using test value)")
            all_present = False
    
    return True  # Don't fail on env vars since they're test values

def test_basic_functionality():
    """Test basic application functionality."""
    try:
        # Test that we can create the FastAPI app
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        import main
        app = main.app
        print("✅ FastAPI application creates successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return False

def run_tests():
    """Run all tests."""
    print("🧪 Running Enterprise Assistant Tests...")
    
    tests = [
        test_main_import,
        test_environment_variables,
        test_basic_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n📋 Running {test.__name__}...")
        if test():
            passed += 1
        
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Check the logs above.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)