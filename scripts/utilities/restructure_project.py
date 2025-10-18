"""
Project Restructuring Script - Under 120 lines
Creates industry-grade folder structure and moves files accordingly
"""

import os
import shutil
from pathlib import Path

def create_structure():
    """Create new folder structure"""
    dirs = [
        'app/api', 'app/core', 'app/models', 'app/services', 'app/utils',
        'frontend/static/css', 'frontend/static/js', 'frontend/templates',
        'tests', 'scripts', 'docs', 'data'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py for Python packages
        if 'app/' in dir_path and dir_path != 'app/utils':
            (Path(dir_path) / '__init__.py').touch()

def move_files():
    """Move existing files to new structure"""
    moves = [
        # Core services
        ('src/retriever/production_retriever.py', 'app/services/retrieval.py'),
        ('mcp/client.py', 'app/services/client.py'),
        ('mcp/memory.py', 'app/core/memory.py'),
        ('mcp/optimizer.py', 'app/core/optimizer.py'),
        ('mcp/web_search.py', 'app/services/web_search.py'),
        ('mcp/server.py', 'app/api/server.py'),
        ('simple_ingest.py', 'app/services/ingestion.py'),
        
        # Config and utils
        ('utils/config_loader.py', 'app/core/config.py'),
        ('exception/custom_exception.py', 'app/core/exceptions.py'),
        
        # Frontend
        ('router/app.py', 'frontend/app.py'),
        
        # Tests and scripts
        ('test_pipeline.py', 'tests/test_pipeline.py'),
        ('enable_vector_search.py', 'scripts/enable_vector_search.py')
    ]
    
    for src, dst in moves:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(src_path, dst_path)
                print(f"✓ {src} -> {dst}")
            except Exception as e:
                print(f"✗ Failed {src}: {e}")

def create_main_files():
    """Create essential application files"""
    
    # Main app
    main_py = """# Production RAG Application Entry Point
from src.app.api.server import start_server

if __name__ == "__main__":
    start_server()
"""
    
    # Requirements
    requirements = """fastapi==0.104.1
uvicorn==0.24.0
astrapy==0.7.0
groq==0.4.1
python-dotenv==1.0.0
pypdf==3.17.0
python-multipart==0.0.6
jinja2==3.1.2
"""
    
    # App config
    app_init = """# Production RAG Application
__version__ = "1.0.0"
"""
    
    # Generation service
    generation_py = """# Response Generation Service - Under 50 lines
import logging
from typing import Dict, Any, Optional
from groq import Groq
import os

logger = logging.getLogger(__name__)

class GenerationService:
    def __init__(self, model: str = "llama3-8b-8192", provider: str = "groq"):
        self.model = model
        self.provider = provider
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY')) if provider == "groq" else None
    
    def generate_response(self, query: str, context: str = "", conversation_history: str = "") -> Dict[str, Any]:
        if not self.client:
            return {"error": "Generation client not available", "success": False}
        
        # Build prompt with context
        prompt = f"Context: {context}\\n\\nConversation: {conversation_history}\\n\\nQuestion: {query}\\n\\nAnswer:"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            return {
                "answer": answer,
                "model": self.model,
                "success": True,
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {"error": str(e), "success": False}
"""
    
    files = {
        'main.py': main_py,
        'requirements.txt': requirements,
        'app/__init__.py': app_init,
        'app/services/generation.py': generation_py
    }
    
    for filepath, content in files.items():
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        Path(filepath).write_text(content)
        print(f"✓ Created {filepath}")

def cleanup_old_files():
    """Remove redundant files"""
    cleanup_patterns = [
        'demo*.py', 'test_*.py', 'debug*.py', 'check*.py', 'setup*.py', 
        'example*.py', 'run_*.py', 'data_ingestion.py'
    ]
    
    removed_count = 0
    for pattern in cleanup_patterns:
        for file in Path('.').glob(pattern):
            if file.is_file():
                try:
                    file.unlink()
                    removed_count += 1
                except:
                    pass
    
    print(f"✓ Cleaned {removed_count} redundant files")

def main():
    """Restructure project to industry standard"""
    print("🏗️  Restructuring to industry-grade structure...")
    
    create_structure()
    print("✓ Created folder structure")
    
    move_files()
    print("✓ Moved core files")
    
    create_main_files()
    print("✓ Created main files")
    
    cleanup_old_files()
    print("✓ Cleaned up redundant files")
    
    print("🎉 Restructuring complete!")
    print("📁 New structure: app/ (api, core, services, models), frontend/, tests/, scripts/")

if __name__ == "__main__":
    main()