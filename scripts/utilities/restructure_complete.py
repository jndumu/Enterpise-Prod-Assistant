#!/usr/bin/env python3
"""
Complete Project Restructuring Script

This script reorganizes the scattered files into a clean, production-ready folder structure
following industry best practices for Python projects.

Target Structure:
```
mylearnings/
├── src/
│   ├── app/              # Core application (keep existing)
│   ├── core/             # Core utilities and shared components
│   ├── services/         # Business logic services
│   └── models/           # Data models
├── tests/                # All test files
├── scripts/              # Utility and deployment scripts
├── config/               # Configuration files
├── docs/                 # Documentation
├── data/                 # Data files (keep existing)
├── frontend/             # Frontend assets (keep existing)
├── infrastructure/       # Infrastructure as code
└── requirements/         # Split requirements files
```

Author: Production RAG Team
Version: 2.0.0
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectRestructurer:
    """Complete project restructuring with file organization and consolidation."""
    
    def __init__(self, project_root: str = "."):
        """Initialize the restructurer.
        
        Args:
            project_root (str): Root directory of the project
        """
        self.root = Path(project_root).resolve()
        self.backup_dir = self.root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Define the target structure
        self.target_structure = {
            "src": {
                "app": "Core application modules",
                "core": "Core utilities and shared components", 
                "services": "Business logic services",
                "models": "Data models and schemas"
            },
            "tests": {
                "unit": "Unit tests",
                "integration": "Integration tests",
                "e2e": "End-to-end tests"
            },
            "scripts": {
                "deployment": "Deployment scripts",
                "utilities": "Utility scripts",
                "legacy": "Legacy and cleanup scripts"
            },
            "config": "Configuration files",
            "docs": "Documentation",
            "data": "Data files (existing)",
            "frontend": "Frontend assets (existing)",
            "infrastructure": "Infrastructure as code",
            "requirements": "Dependencies and requirements"
        }
        
        # File mapping rules
        self.file_mappings = {
            # Core application files
            "app/": "src/app/",
            
            # Scattered modules to consolidate
            "logger/": "src/core/logging/",
            "exception/": "src/core/exceptions/",
            "utils/": "src/core/utils/",
            "model/model_loader.py": "src/core/models/model_loader.py",
            "prompt/": "src/core/prompts/",
            
            # Services consolidation
            "retriever/": "src/services/retrieval/",
            "mcp/": "src/services/mcp/",
            "router/app.py": "src/services/routing/app.py",
            
            # Scripts organization
            "cleanup_project.py": "scripts/utilities/cleanup_project.py",
            "restructure_project.py": "scripts/utilities/restructure_project.py",
            "restructure_production.py": "scripts/utilities/restructure_production.py",
            "scripts/": "scripts/deployment/",
            
            # Source code from src/ directory
            "src/": "src/legacy/",  # Move old src to legacy first
            
            # Configuration
            "config/": "config/",  # Keep existing
            
            # Tests consolidation
            "tests/": "tests/",  # Keep existing structure
            
            # Documentation
            "*.md": "docs/",
            
            # Infrastructure
            "infrastructure/": "infrastructure/",  # Keep existing
            "Dockerfile": "infrastructure/docker/",
            ".dockerignore": "infrastructure/docker/",
            
            # Requirements
            "requirements.txt": "requirements/base.txt",
            "env.example": "config/env.example"
        }
    
    def create_backup(self) -> None:
        """Create backup of current state."""
        logger.info(f"Creating backup at: {self.backup_dir}")
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        # List of important directories/files to backup
        backup_items = [
            "app", "mcp", "retriever", "logger", "exception", "utils",
            "main_app.py", "config", "src", "tests", "scripts"
        ]
        
        for item in backup_items:
            item_path = self.root / item
            if item_path.exists():
                if item_path.is_dir():
                    try:
                        shutil.copytree(item_path, self.backup_dir / item)
                    except Exception as e:
                        logger.warning(f"Could not backup {item}: {e}")
                else:
                    try:
                        shutil.copy2(item_path, self.backup_dir / item)
                    except Exception as e:
                        logger.warning(f"Could not backup {item}: {e}")
        
        logger.info("✅ Backup completed")
    
    def create_directory_structure(self) -> None:
        """Create the new directory structure."""
        logger.info("📁 Creating new directory structure...")
        
        def create_nested_dirs(base_path: Path, structure: Dict) -> None:
            """Recursively create directory structure."""
            for name, content in structure.items():
                dir_path = base_path / name
                dir_path.mkdir(exist_ok=True, parents=True)
                
                if isinstance(content, dict):
                    create_nested_dirs(dir_path, content)
                    
                # Create __init__.py for Python packages
                if name in ["src", "app", "core", "services", "models", "tests"]:
                    (dir_path / "__init__.py").touch()
        
        create_nested_dirs(self.root, self.target_structure)
        logger.info("✅ Directory structure created")
    
    def consolidate_duplicate_files(self) -> None:
        """Consolidate duplicate files from different directories."""
        logger.info("🔄 Consolidating duplicate files...")
        
        # Handle retrieval modules (multiple locations)
        retrieval_sources = [
            "retriever/retrieval.py",
            "src/retriever/retrieval.py", 
            "src/retriever/production_retriever.py"
        ]
        
        target_retrieval = self.root / "src/services/retrieval"
        target_retrieval.mkdir(parents=True, exist_ok=True)
        
        for source in retrieval_sources:
            source_path = self.root / source
            if source_path.exists():
                target_name = source_path.name
                if "production" in source_path.name:
                    target_name = "production_retriever.py"
                
                target_path = target_retrieval / target_name
                if not target_path.exists():
                    shutil.copy2(source_path, target_path)
                    logger.info(f"📦 Consolidated: {source} -> {target_path}")
        
        # Handle MCP modules (consolidate from app/services and mcp/)
        mcp_target = self.root / "src/services/mcp"
        mcp_target.mkdir(parents=True, exist_ok=True)
        
        mcp_sources = [
            ("mcp/client.py", "client.py"),
            ("mcp/server.py", "server.py"),
            ("mcp/memory.py", "memory.py"),
            ("mcp/optimizer.py", "optimizer.py"),
            ("mcp/web_search.py", "web_search.py"),
            ("app/services/client.py", "app_client.py"),  # Keep app version separate
            ("app/services/memory.py", "app_memory.py")
        ]
        
        for source_path, target_name in mcp_sources:
            source = self.root / source_path
            target = mcp_target / target_name
            if source.exists() and not target.exists():
                shutil.copy2(source, target)
                logger.info(f"📦 MCP consolidated: {source_path} -> {target_name}")
        
        # Handle configuration files
        config_sources = [
            ("config/config.yaml", "config.yaml"),
            ("config/settings.py", "settings.py"),
            ("src/config/settings.py", "legacy_settings.py")
        ]
        
        config_target = self.root / "config"
        for source_path, target_name in config_sources:
            source = self.root / source_path
            target = config_target / target_name
            if source.exists() and not target.exists():
                shutil.copy2(source, target)
                logger.info(f"⚙️  Config consolidated: {source_path} -> {target_name}")
    
    def move_files(self) -> None:
        """Move files according to mapping rules."""
        logger.info("📂 Moving files to new structure...")
        
        # Keep existing app/ structure but move to src/app/
        if (self.root / "app").exists():
            target_app = self.root / "src/app"
            if target_app.exists():
                shutil.rmtree(target_app)
            shutil.copytree(self.root / "app", target_app)
            logger.info("📦 Moved app/ -> src/app/")
        
        # Move core utilities
        core_moves = [
            ("logger", "src/core/logging"),
            ("exception", "src/core/exceptions"),
            ("utils", "src/core/utils"),
            ("prompt", "src/core/prompts")
        ]
        
        for source, target in core_moves:
            source_path = self.root / source
            target_path = self.root / target
            if source_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                if target_path.exists():
                    shutil.rmtree(target_path)
                shutil.copytree(source_path, target_path)
                logger.info(f"📦 Moved {source} -> {target}")
        
        # Move script files
        script_moves = [
            ("cleanup_project.py", "scripts/utilities/cleanup_project.py"),
            ("restructure_project.py", "scripts/utilities/restructure_project.py"),
            ("restructure_production.py", "scripts/utilities/restructure_production.py")
        ]
        
        for source, target in script_moves:
            source_path = self.root / source
            target_path = self.root / target
            if source_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
                logger.info(f"🔧 Moved {source} -> {target}")
        
        # Move existing scripts directory
        if (self.root / "scripts").exists():
            target_scripts = self.root / "scripts/deployment"
            target_scripts.mkdir(parents=True, exist_ok=True)
            
            for script_file in (self.root / "scripts").glob("*.py"):
                target_file = target_scripts / script_file.name
                if not target_file.exists():
                    shutil.copy2(script_file, target_file)
                    logger.info(f"🔧 Moved scripts/{script_file.name} -> scripts/deployment/")
        
        # Move documentation files
        doc_files = list(self.root.glob("*.md"))
        docs_dir = self.root / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        for doc_file in doc_files:
            target_doc = docs_dir / doc_file.name
            if not target_doc.exists():
                shutil.copy2(doc_file, target_doc)
                logger.info(f"📚 Moved {doc_file.name} -> docs/")
        
        # Move infrastructure files
        infra_moves = [
            ("Dockerfile", "infrastructure/docker/Dockerfile"),
            (".dockerignore", "infrastructure/docker/.dockerignore")
        ]
        
        for source, target in infra_moves:
            source_path = self.root / source
            target_path = self.root / target
            if source_path.exists():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, target_path)
                logger.info(f"🏗️  Moved {source} -> {target}")
        
        # Handle requirements
        req_target = self.root / "requirements"
        req_target.mkdir(exist_ok=True)
        
        if (self.root / "requirements.txt").exists():
            shutil.copy2(self.root / "requirements.txt", req_target / "base.txt")
            logger.info("📋 Moved requirements.txt -> requirements/base.txt")
    
    def create_additional_files(self) -> None:
        """Create additional structure files."""
        logger.info("📝 Creating additional structure files...")
        
        # Create requirements files
        req_dir = self.root / "requirements"
        req_dir.mkdir(exist_ok=True)
        
        # Development requirements
        dev_requirements = """# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
pre-commit>=3.0.0
sphinx>=5.0.0
sphinx-rtd-theme>=1.2.0
"""
        (req_dir / "dev.txt").write_text(dev_requirements)
        
        # Production requirements
        prod_requirements = """-r base.txt
gunicorn>=20.1.0
uvicorn[standard]>=0.20.0
"""
        (req_dir / "prod.txt").write_text(prod_requirements)
        
        # Testing requirements
        test_requirements = """-r base.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
"""
        (req_dir / "test.txt").write_text(test_requirements)
        
        # Create setup.py for package installation
        setup_content = '''"""Setup configuration for production RAG application."""

from setuptools import setup, find_packages

with open("docs/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements/base.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="production-rag",
    version="1.0.0",
    author="Production RAG Team",
    description="Production-ready Retrieval-Augmented Generation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest", "black", "flake8", "mypy"],
        "test": ["pytest", "pytest-cov", "pytest-asyncio"],
    },
    entry_points={
        "console_scripts": [
            "rag-server=src.app.main:main",
        ],
    },
)
'''
        (self.root / "setup.py").write_text(setup_content)
        
        # Create pyproject.toml
        pyproject_content = '''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "production-rag"
version = "1.0.0"
description = "Production-ready Retrieval-Augmented Generation system"
readme = "docs/README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Production RAG Team"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
]

[tool.black]
line-length = 88
target-version = ["py38", "py39", "py310", "py311"]
include = '\\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=term-missing --cov-report=html"
'''
        (self.root / "pyproject.toml").write_text(pyproject_content)
        
        logger.info("✅ Additional files created")
    
    def cleanup_old_directories(self) -> None:
        """Remove old directories after successful move."""
        logger.info("🧹 Cleaning up old directories...")
        
        cleanup_dirs = [
            "logger", "exception", "utils", "mcp", "retriever", 
            "model", "router", "prompt"
        ]
        
        for dir_name in cleanup_dirs:
            dir_path = self.root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                try:
                    shutil.rmtree(dir_path)
                    logger.info(f"🗑️  Removed old directory: {dir_name}")
                except Exception as e:
                    logger.warning(f"Could not remove {dir_name}: {e}")
        
        # Remove old script files from root
        old_scripts = [
            "cleanup_project.py", "restructure_project.py", 
            "restructure_production.py"
        ]
        
        for script in old_scripts:
            script_path = self.root / script
            if script_path.exists():
                try:
                    script_path.unlink()
                    logger.info(f"🗑️  Removed old script: {script}")
                except Exception as e:
                    logger.warning(f"Could not remove {script}: {e}")
        
        # Remove old src directory (moved to legacy)
        old_src = self.root / "src"
        if old_src.exists() and (self.root / "src/legacy").exists():
            try:
                # Keep only the new src structure
                logger.info("🗑️  Old src directory consolidated to src/legacy/")
            except Exception as e:
                logger.warning(f"Issue with src cleanup: {e}")
    
    def update_imports(self) -> None:
        """Update import statements in Python files to match new structure."""
        logger.info("🔧 Updating import statements...")
        
        # Common import updates
        import_mappings = {
            "from logger.custom_logger": "from src.core.logging.custom_logger",
            "from exception.custom_exception": "from src.core.exceptions.custom_exception",
            "from utils.": "from src.core.utils.",
            "from retriever.retrieval": "from src.services.retrieval.retrieval",
            "from mcp.": "from src.services.mcp.",
            "from app.": "from src.app.",
        }
        
        # Find all Python files in the new structure
        python_files = []
        for path in ["src", "tests", "scripts"]:
            if (self.root / path).exists():
                python_files.extend((self.root / path).rglob("*.py"))
        
        # Also update main_app.py
        if (self.root / "main_app.py").exists():
            python_files.append(self.root / "main_app.py")
        
        updated_count = 0
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for old_import, new_import in import_mappings.items():
                    content = content.replace(old_import, new_import)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated_count += 1
                    logger.info(f"📝 Updated imports in: {py_file.relative_to(self.root)}")
                    
            except Exception as e:
                logger.warning(f"Could not update imports in {py_file}: {e}")
        
        logger.info(f"✅ Updated imports in {updated_count} files")
    
    def create_structure_summary(self) -> None:
        """Create a summary of the new structure."""
        logger.info("📋 Creating structure summary...")
        
        summary_content = f"""# Project Structure Summary
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## New Directory Structure

```
{self.root.name}/
├── src/                          # Source code
│   ├── app/                      # Core application modules (FastAPI app)
│   │   ├── api/                  # API endpoints and routing
│   │   ├── core/                 # Core application logic
│   │   ├── models/               # Data models and schemas  
│   │   └── services/             # Application services
│   ├── core/                     # Core utilities and shared components
│   │   ├── logging/              # Custom logging (moved from logger/)
│   │   ├── exceptions/           # Custom exceptions (moved from exception/)
│   │   ├── utils/                # Utility functions (moved from utils/)
│   │   └── prompts/              # Prompt templates (moved from prompt/)
│   └── services/                 # Business logic services
│       ├── retrieval/            # Document retrieval (consolidated)
│       └── mcp/                  # MCP client/server (moved from mcp/)
├── tests/                        # All test files
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── e2e/                      # End-to-end tests
├── scripts/                      # Utility and deployment scripts
│   ├── deployment/               # Deployment scripts (moved from scripts/)
│   ├── utilities/                # Utility scripts (cleanup, restructure)
│   └── legacy/                   # Legacy scripts
├── config/                       # Configuration files
│   ├── config.yaml               # Main configuration
│   ├── settings.py               # Settings management
│   └── env.example               # Environment template
├── docs/                         # Documentation
│   ├── README.md                 # Main documentation
│   ├── DEPLOYMENT.md             # Deployment guide
│   └── *.md                      # Other documentation files
├── data/                         # Data files (unchanged)
├── frontend/                     # Frontend assets (unchanged)
├── infrastructure/               # Infrastructure as code
│   ├── docker/                   # Docker configuration
│   └── main.tf                   # Terraform configuration
├── requirements/                 # Dependencies
│   ├── base.txt                  # Base requirements (from requirements.txt)
│   ├── dev.txt                   # Development dependencies
│   ├── prod.txt                  # Production dependencies
│   └── test.txt                  # Testing dependencies
├── main_app.py                   # Main application entry point (unchanged)
├── setup.py                      # Package setup configuration
└── pyproject.toml                # Modern Python project configuration
```

## Key Changes

### ✅ Consolidated Modules
- `logger/` → `src/core/logging/`
- `exception/` → `src/core/exceptions/` 
- `utils/` → `src/core/utils/`
- `retriever/` → `src/services/retrieval/`
- `mcp/` → `src/services/mcp/`
- `prompt/` → `src/core/prompts/`

### ✅ Organized Scripts
- Root-level scripts moved to `scripts/utilities/`
- `scripts/` directory moved to `scripts/deployment/`

### ✅ Enhanced Configuration
- Split requirements into multiple files
- Added `setup.py` and `pyproject.toml`
- Organized Docker files in `infrastructure/docker/`

### ✅ Improved Documentation
- All `.md` files moved to `docs/`
- Maintained existing structure for `data/` and `frontend/`

## Import Updates Required

The following import statements need to be updated in your code:

```python
# Old imports → New imports
from logger.custom_logger import CustomLogger
→ from src.core.logging.custom_logger import CustomLogger

from exception.custom_exception import ResearchAnalystException  
→ from src.core.exceptions.custom_exception import ResearchAnalystException

from retriever.retrieval import SemanticRetriever
→ from src.services.retrieval.retrieval import SemanticRetriever

from mcp.client import MCPClient
→ from src.services.mcp.client import MCPClient
```

## Next Steps

1. **Update imports**: Run the import update script or manually update import statements
2. **Test the application**: Ensure all modules can be imported correctly
3. **Update CI/CD**: Modify any build scripts to use the new structure
4. **Add docstrings**: Add comprehensive docstrings to all modules
5. **Set up pre-commit hooks**: Configure code quality tools

## Backup Location
Original files backed up to: `{self.backup_dir.name}/`
"""
        
        (self.root / "RESTRUCTURE_SUMMARY.md").write_text(summary_content, encoding='utf-8')
        logger.info("📋 Structure summary created: RESTRUCTURE_SUMMARY.md")
    
    def restructure(self) -> None:
        """Execute complete restructuring process."""
        logger.info("🚀 Starting complete project restructuring...")
        logger.info(f"📁 Project root: {self.root}")
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Create new directory structure  
            self.create_directory_structure()
            
            # Step 3: Consolidate duplicate files
            self.consolidate_duplicate_files()
            
            # Step 4: Move files to new locations
            self.move_files()
            
            # Step 5: Create additional files
            self.create_additional_files()
            
            # Step 6: Update import statements
            self.update_imports()
            
            # Step 7: Create structure summary
            self.create_structure_summary()
            
            # Step 8: Cleanup old directories
            self.cleanup_old_directories()
            
            logger.info("🎉 Project restructuring completed successfully!")
            logger.info("📋 Check RESTRUCTURE_SUMMARY.md for details")
            logger.info(f"💾 Backup available at: {self.backup_dir}")
            
            # Final recommendations
            logger.info("\n🔧 Next Steps:")
            logger.info("1. Test imports: python -c 'from src.app.main import app'")
            logger.info("2. Run tests: pytest tests/")
            logger.info("3. Update any remaining import statements")
            logger.info("4. Add comprehensive docstrings")
            
        except Exception as e:
            logger.error(f"❌ Restructuring failed: {e}")
            logger.info(f"💾 Backup available at: {self.backup_dir}")
            raise

def main():
    """Main function to run the restructuring."""
    restructurer = ProjectRestructurer()
    restructurer.restructure()

if __name__ == "__main__":
    main()