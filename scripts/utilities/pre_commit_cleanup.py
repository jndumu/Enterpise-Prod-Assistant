#!/usr/bin/env python3
"""
Pre-commit Cleanup Script

This script cleans up temporary files, backup directories, and other items
that shouldn't be committed to GitHub.

Usage: python scripts/utilities/pre_commit_cleanup.py

Author: Production RAG Team
Version: 1.0.0
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def cleanup_project(project_root: str = ".") -> None:
    """Clean up project before committing to GitHub."""
    root = Path(project_root).resolve()
    logger.info(f"🧹 Cleaning up project at: {root}")
    
    # Items to clean up
    cleanup_patterns = [
        "backup_*",
        "archived_files_*.zip",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.tmp",
        ".pytest_cache",
        "htmlcov",
        "*.log",
        "logs/*",
        "test_env",
    ]
    
    cleanup_count = 0
    
    for pattern in cleanup_patterns:
        if "*" in pattern:
            # Handle glob patterns
            matches = list(root.glob(pattern))
            matches.extend(list(root.glob(f"**/{pattern}")))
        else:
            # Handle direct paths
            matches = [root / pattern] if (root / pattern).exists() else []
        
        for item in matches:
            if item.exists():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                        logger.info(f"🗑️  Removed directory: {item.name}")
                    else:
                        item.unlink()
                        logger.info(f"🗑️  Removed file: {item.name}")
                    cleanup_count += 1
                except Exception as e:
                    logger.warning(f"⚠️  Could not remove {item}: {e}")
    
    logger.info(f"✅ Cleanup complete: {cleanup_count} items removed")

def main():
    """Main function."""
    print("🧹 Pre-commit Cleanup")
    print("=" * 30)
    
    cleanup_project()
    
    print("\n🎯 Project is clean and ready for GitHub commit!")
    print("\nNext steps:")
    print("1. git add .")
    print("2. git commit -m 'feat: initial production RAG application'")
    print("3. git push origin main")

if __name__ == "__main__":
    main()