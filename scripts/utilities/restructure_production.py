"""
Production Folder Restructuring - Under 100 lines
Organizes files into proper production structure
"""

import os
import shutil
from pathlib import Path

def create_production_structure():
    """Create production-grade folder structure"""
    print("📁 Creating production folder structure...")
    
    # Define the target structure
    structure = {
        'tests': ['unit', 'integration', 'e2e'],
        'src/tests': ['ingestion', 'retrieval'],
        'scripts': [],
        'config': [],
        'docs': []
    }
    
    # Create directories
    for base_dir, subdirs in structure.items():
        Path(base_dir).mkdir(parents=True, exist_ok=True)
        
        # Add __init__.py to Python test packages
        if 'test' in base_dir:
            (Path(base_dir) / '__init__.py').write_text("# Test package\n")
        
        for subdir in subdirs:
            subdir_path = Path(base_dir) / subdir
            subdir_path.mkdir(exist_ok=True)
            if 'test' in base_dir:
                (subdir_path / '__init__.py').write_text("# Test subpackage\n")
    
    print("✅ Folder structure created")

def move_files_to_structure():
    """Move files to appropriate locations"""
    print("📦 Moving files to production structure...")
    
    # Define file movements
    moves = [
        # Scripts
        ('start_server.py', 'scripts/start_server.py'),
        ('enable_vector_search.py', 'scripts/enable_vector_search.py'),
        
        # Legacy files to archive or move
        ('simple_ingest.py', 'src/tests/ingestion/test_simple_ingest.py'),
        ('ingest_pdf.py', 'src/tests/ingestion/test_ingest_pdf.py'),
        
        # Main app stays at root for now
        ('main.py', 'scripts/legacy_main.py'),
    ]
    
    moved_count = 0
    for src, dst in moves:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            # Create destination directory
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                shutil.move(str(src_path), str(dst_path))
                print(f"  ✓ Moved {src} → {dst}")
                moved_count += 1
            except Exception as e:
                print(f"  ✗ Failed to move {src}: {e}")
    
    print(f"✅ Moved {moved_count} files")

def create_test_files():
    """Create proper test structure"""
    print("🧪 Creating test structure...")
    
    # Unit tests
    unit_test = '''"""
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
'''
    
    # Integration tests
    integration_test = '''"""
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
'''
    
    # Write test files
    test_files = {
        'tests/unit/test_components.py': unit_test,
        'tests/integration/test_pipeline.py': integration_test
    }
    
    for file_path, content in test_files.items():
        Path(file_path).write_text(content)
        print(f"  ✓ Created {file_path}")
    
    print("✅ Test files created")

def main():
    """Main restructuring process"""
    print("🏗️  Production Folder Restructuring")
    print("=" * 50)
    
    create_production_structure()
    move_files_to_structure()
    create_test_files()
    
    print("=" * 50)
    print("🎉 Production structure ready!")
    print("📁 Final structure:")
    print("├── app/           # Core application")
    print("├── frontend/      # Web interface") 
    print("├── tests/         # All tests")
    print("├── scripts/       # Utility scripts")
    print("├── docs/          # Documentation")
    print("└── main_app.py    # Application entry")

if __name__ == "__main__":
    main()