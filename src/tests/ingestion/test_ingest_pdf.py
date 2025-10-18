"""
Ultra-compact PDF ingestion for AstraDB vector store.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import PyPDF2
except ImportError:
    os.system("pip install PyPDF2")
    import PyPDF2

from src.services.retrieval.retrieval import SemanticRetriever

logger = logging.getLogger(__name__)

class CompactPDFIngester:
    """Ultra-compact PDF processor."""
    
    def __init__(self, chunk_size: int = 800):
        self.chunk_size = chunk_size
        self.retriever = SemanticRetriever()
    
    def extract_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF."""
        try:
            with open(pdf_path, 'rb') as file:
                text = ""
                for page in PyPDF2.PdfReader(file).pages:
                    text += page.extract_text() + " "
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""
    
    def chunk_text(self, text: str, source: str) -> list:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size):
            chunk = " ".join(words[i:i + self.chunk_size])
            if len(chunk) > 100:  # Skip tiny chunks
                chunks.append({
                    "content": chunk,
                    "metadata": {
                        "source": source,
                        "chunk": len(chunks),
                        "type": "pdf"
                    }
                })
        return chunks
    
    def process_pdf(self, pdf_path: str) -> int:
        """Process single PDF file."""
        filename = Path(pdf_path).name
        print(f"Processing {filename}...")
        
        text = self.extract_pdf(pdf_path)
        if not text:
            print(f"❌ No text from {filename}")
            return 0
        
        chunks = self.chunk_text(text, filename)
        stored = 0
        
        for chunk in chunks:
            if self.retriever.insert_document(chunk["content"], chunk["metadata"]):
                stored += 1
        
        print(f"✅ {filename}: {stored} chunks stored")
        return stored
    
    def ingest_folder(self, folder: str = "data") -> dict:
        """Process all PDFs in folder."""
        path = Path(folder)
        pdfs = list(path.glob("*.pdf"))
        
        if not pdfs:
            print(f"❌ No PDFs found in {folder}")
            return {}
        
        results = {}
        for pdf in pdfs:
            results[pdf.name] = self.process_pdf(str(pdf))
        
        return results

def main():
    """Run PDF ingestion."""
    print("🔄 PDF Ingestion Starting...")
    
    ingester = CompactPDFIngester()
    
    # Check connection
    stats = ingester.retriever.get_stats()
    print(f"📊 Current documents: {stats.get('document_count', 'unknown')}")
    
    # Process PDFs
    results = ingester.ingest_folder()
    
    if results:
        total = sum(results.values())
        print(f"\\n📈 Results:")
        for file, count in results.items():
            print(f"   {file}: {count} chunks")
        print(f"🎯 Total: {total} chunks ingested")
        
        # Final count
        final_stats = ingester.retriever.get_stats()
        print(f"📊 Final count: {final_stats.get('document_count', 'unknown')}")
    else:
        print("❌ No files processed")

if __name__ == "__main__":
    main()