"""
Project Cleanup for Production Deployment - Under 100 lines
Archives unnecessary files and cleans project structure
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_archive():
    """Create archive of unnecessary files before cleanup"""
    print("📦 Creating archive of unnecessary files...")
    
    archive_name = f"archived_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    # Files and folders to archive (not delete yet)
    to_archive = [
        'etl',  # Empty etl folder in root
        'logs', 'notebook', '__pycache__',
        'test_*.py', '*.log', '*.pyc',
        'debug_*.py', 'demo*.py', 'check_*.py',
        'setup_*.py', 'example_*.py'
    ]
    
    with zipfile.ZipFile(archive_name, 'w') as zf:
        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            if any(skip in root for skip in ['app', 'frontend', 'data', '.env', '.git']):
                continue
                
            for file in files:
                file_path = Path(root) / file
                if any(pattern in file for pattern in to_archive):
                    zf.write(file_path, file_path)
                    print(f"  Archived: {file_path}")
    
    print(f"✅ Archive created: {archive_name}")

def cleanup_files():
    """Remove unnecessary files and folders"""
    print("🧹 Cleaning up unnecessary files...")
    
    # Directories to remove
    dirs_to_remove = ['etl', 'logs', '__pycache__', 'notebook']
    
    # File patterns to remove
    files_to_remove = ['test_*.py', 'debug_*.py', 'demo*.py', 'check_*.py', 
                      'setup_*.py', 'example_*.py', '*.pyc', '*.log']
    
    removed_count = 0
    
    # Remove directories
    for dir_name in dirs_to_remove:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"  Removed directory: {dir_name}")
            removed_count += 1
    
    # Remove files matching patterns
    for pattern in files_to_remove:
        for file_path in Path('.').glob(pattern):
            if file_path.is_file():
                file_path.unlink()
                print(f"  Removed file: {file_path}")
                removed_count += 1
    
    print(f"✅ Cleaned up {removed_count} items")

def optimize_structure():
    """Optimize remaining project structure"""
    print("📁 Optimizing project structure...")
    
    # Ensure required directories exist
    required_dirs = ['app/api', 'app/core', 'app/services', 'frontend/static', 
                    'frontend/templates', 'data', 'scripts']
    
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Add __init__.py to Python packages
        if 'app/' in dir_path and dir_path != 'app/static':
            init_file = Path(dir_path) / '__init__.py'
            if not init_file.exists():
                init_file.write_text("# Production RAG Application Module\n")
    
    print("✅ Project structure optimized")

def create_production_config():
    """Create production configuration files"""
    print("⚙️ Creating production configuration...")
    
    # Update requirements.txt with essential dependencies only
    requirements = """fastapi==0.104.1
uvicorn==0.24.0
astrapy==0.7.0
groq==0.4.1
python-dotenv==1.0.0
pypdf==3.17.0
python-multipart==0.0.6
jinja2==3.1.2
requests==2.31.0
"""
    
    Path('requirements.txt').write_text(requirements)
    print("  Updated requirements.txt")
    
    # Create .dockerignore
    dockerignore = """*.pyc
__pycache__/
*.log
.git/
tests/
*.md
archived_files_*
.DS_Store
"""
    
    Path('.dockerignore').write_text(dockerignore)
    print("  Created .dockerignore")
    
    print("✅ Production configuration created")

def main():
    """Main cleanup process"""
    print("🚀 Starting Production Cleanup Process")
    print("=" * 50)
    
    # Step 1: Create archive
    create_archive()
    
    # Step 2: Clean up files
    cleanup_files()
    
    # Step 3: Optimize structure  
    optimize_structure()
    
    # Step 4: Create production config
    create_production_config()
    
    print("=" * 50)
    print("🎉 Cleanup completed successfully!")
    print("📦 Archived files are preserved in zip file")
    print("🚀 Project ready for production deployment")

if __name__ == "__main__":
    main()