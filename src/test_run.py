"""Test run to verify file processing."""
import os
from pathlib import Path
from etl.data_ingestion import PDFIngestion

def main():
    # Get absolute path to data folder
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data"
    
    print(f"Looking for files in: {data_path}")
    
    # List files
    files = list(data_path.glob("*.pdf"))
    print(f"Found PDF files: {[f.name for f in files]}")
    
    # Test ingestion
    ingestion = PDFIngestion()
    results = ingestion.process_folder(str(data_path))
    
    total_chunks = sum(results.values())
    print(f"\n🎯 Results: {total_chunks} chunks from {len(results)} files")
    
    for filename, chunks in results.items():
        status = "✅" if chunks > 0 else "❌"
        print(f"   {status} {filename}: {chunks} chunks")

if __name__ == "__main__":
    main()