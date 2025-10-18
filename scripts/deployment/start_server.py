#!/usr/bin/env python3
"""
Simple server startup script
"""

import subprocess
import sys
import os

def main():
    """Start the RAG application server"""
    print("🚀 Starting Production RAG Server...")
    print("📍 URL: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        # Use uvicorn directly via command line
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main_app:app",
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        print("💡 Try: pip install uvicorn fastapi")

if __name__ == "__main__":
    main()