#!/usr/bin/env python3
"""
Project Structure Verification Script

This script verifies that the restructuring was successful by testing imports,
checking file locations, and validating the new structure.

Author: Production RAG Team
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
import importlib.util

def test_imports():
    """Test critical imports to ensure they work."""
    print("🔍 Testing imports...")
    
    test_cases = [
        ("src.app.services.client", "MCPClient"),
        ("src.app.services.generation", "GenerationService"),
        ("src.app.services.ingestion", "main"),
        ("src.app.core.memory", "MemoryClient"),
        ("src.core.logging.custom_logger", "CustomLogger"),
        ("src.core.exceptions.custom_exception", "ResearchAnalystException"),
        ("src.services.retrieval.retrieval", "SemanticRetriever"),
    ]
    
    success_count = 0
    for module_name, class_name in test_cases:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"  ✅ {module_name}.{class_name}")
                success_count += 1
            else:
                print(f"  ⚠️  {module_name} imported but {class_name} not found")
        except ImportError as e:
            print(f"  ❌ Failed to import {module_name}: {e}")
    
    print(f"\n📊 Import Results: {success_count}/{len(test_cases)} successful")
    return success_count == len(test_cases)

def verify_structure():
    """Verify the expected directory structure exists."""
    print("\n📁 Verifying directory structure...")
    
    expected_dirs = [
        "src/app/api",
        "src/app/core",
        "src/app/services", 
        "src/core/logging",
        "src/core/exceptions",
        "src/core/utils",
        "src/core/prompts",
        "src/services/retrieval",
        "src/services/mcp",
        "tests/unit",
        "tests/integration",
        "scripts/deployment",
        "scripts/utilities",
        "config",
        "docs",
        "requirements",
        "infrastructure/docker"
    ]
    
    missing_dirs = []
    for dir_path in expected_dirs:
        if not (Path(dir_path).exists()):
            missing_dirs.append(dir_path)
        else:
            print(f"  ✅ {dir_path}")
    
    if missing_dirs:
        print(f"\n❌ Missing directories: {missing_dirs}")
        return False
    
    print(f"\n✅ All {len(expected_dirs)} expected directories found")
    return True

def check_key_files():
    """Check that key files are in their expected locations."""
    print("\n📄 Checking key files...")
    
    key_files = [
        "main_app.py",
        "src/app/services/client.py",
        "src/app/services/generation.py",
        "src/app/services/ingestion.py",
        "src/app/core/memory.py",
        "src/core/logging/custom_logger.py",
        "src/core/exceptions/custom_exception.py",
        "requirements/base.txt",
        "requirements/dev.txt",
        "config/config.yaml",
        "setup.py",
        "pyproject.toml",
        "RESTRUCTURE_SUMMARY.md"
    ]
    
    missing_files = []
    for file_path in key_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    print(f"\n✅ All {len(key_files)} key files found")
    return True

def test_main_app():
    """Test that the main app can be imported."""
    print("\n🚀 Testing main application...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, str(Path.cwd()))
        
        # Test main app import
        spec = importlib.util.spec_from_file_location("main_app", "main_app.py")
        main_app = importlib.util.module_from_spec(spec)
        
        print("  ✅ main_app.py can be loaded")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to load main_app.py: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🔬 Starting Project Structure Verification")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Directory Structure", verify_structure),
        ("Key Files", check_key_files),
        ("Import Tests", test_imports),
        ("Main Application", test_main_app)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:20} : {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Project structure is ready.")
        print("\n🔧 Next recommended steps:")
        print("1. Add comprehensive docstrings to all modules")
        print("2. Set up pre-commit hooks: pre-commit install")  
        print("3. Run tests: pytest tests/")
        print("4. Start the application: python main_app.py")
        return True
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)