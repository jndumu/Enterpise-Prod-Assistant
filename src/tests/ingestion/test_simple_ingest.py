"""
Simple PDF and text file ingestion using existing components.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Install dependencies if needed
try:
    import PyPDF2
except ImportError:
    print("Installing PyPDF2...")
    os.system("pip install PyPDF2")
    import PyPDF2

from src.services.retrieval.retrieval import SemanticRetriever

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def extract_text_file(txt_path: str) -> str:
    """Extract text from text file."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading text file {txt_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 800) -> list:
    """Split text into chunks."""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.strip()) > 100:  # Skip very small chunks
            chunks.append(chunk.strip())
    
    return chunks

def ingest_file(file_path: Path, retriever: SemanticRetriever) -> int:
    """Ingest a single file."""
    print(f"Processing {file_path.name}...")
    
    # Extract text based on file type
    if file_path.suffix.lower() == '.pdf':
        text = extract_pdf_text(str(file_path))
    elif file_path.suffix.lower() in ['.txt', '.md']:
        text = extract_text_file(str(file_path))
    else:
        print(f"Skipping unsupported file type: {file_path.suffix}")
        return 0
    
    if not text:
        print(f"No text extracted from {file_path.name}")
        return 0
    
    # Chunk the text
    chunks = chunk_text(text)
    if not chunks:
        print(f"No chunks created from {file_path.name}")
        return 0
    
    # Store chunks
    stored_count = 0
    for i, chunk in enumerate(chunks):
        metadata = {
            "source": file_path.name,
            "chunk_index": i,
            "file_type": file_path.suffix,
            "total_chunks": len(chunks)
        }
        
        success = retriever.insert_document(chunk, metadata)
        if success:
            stored_count += 1
    
    print(f"✅ {file_path.name}: {stored_count}/{len(chunks)} chunks stored")
    return stored_count

def main():
    """Main ingestion process."""
    print("🔄 Simple Data Ingestion Starting...")
    
    # Initialize retriever
    retriever = SemanticRetriever(collection_name="semantic_data")
    
    # Check connection
    stats = retriever.get_stats()
    if "error" in stats:
        print(f"❌ Vector store error: {stats['error']}")
        return
    
    print(f"✅ Connected to collection: {stats['collection_name']}")
    print(f"📊 Current documents: {stats['document_count']}")
    
    # Find files to process
    data_folder = Path("data")
    if not data_folder.exists():
        print("❌ Data folder not found")
        return
    
    # Process supported files
    supported_files = []
    for ext in ['.pdf', '.txt', '.md']:
        supported_files.extend(data_folder.glob(f"*{ext}"))
    
    if not supported_files:
        print("❌ No supported files found in data folder")
        return
    
    print(f"📁 Found {len(supported_files)} files to process")
    
    total_chunks = 0
    successful_files = 0
    
    for file_path in supported_files:
        try:
            chunks_stored = ingest_file(file_path, retriever)
            if chunks_stored > 0:
                total_chunks += chunks_stored
                successful_files += 1
        except Exception as e:
            print(f"❌ Failed to process {file_path.name}: {e}")
    
    # Final summary
    print(f"\\n🎯 Ingestion Summary:")
    print(f"   Files processed: {successful_files}/{len(supported_files)}")
    print(f"   Total chunks: {total_chunks}")
    
    # Verify final state
    final_stats = retriever.get_stats()
    print(f"📊 Final document count: {final_stats.get('document_count', 'unknown')}")
    
    # Test search
    if total_chunks > 0:
        print("\\n🔍 Testing search...")
        results = retriever.search("machine learning", limit=2)
        if results:
            print(f"✅ Search test: Found {len(results)} results")
            print(f"   Sample: {results[0].content[:100]}...")
        else:
            print("⚠️  Search test: No results found")

if __name__ == "__main__":
    main()