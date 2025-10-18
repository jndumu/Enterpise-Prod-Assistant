#!/usr/bin/env python3
"""
Quick start script for Enterprise Production Assistant
"""

import sys
import os
import subprocess

def main():
    """Start the Enterprise Production Assistant"""
    print("🚀 Starting Enterprise Production Assistant...")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating from template...")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("📝 Created .env from template. Please configure your API keys.")
        else:
            print("❌ No .env.example found. Please create .env file.")
            return
    
    # Add app to Python path
    sys.path.append('app')
    
    try:
        # Import and start server
        from app.api.server import start_server
        print("✅ Starting server on http://localhost:8000")
        start_server()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()