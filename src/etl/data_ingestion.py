"""Optimized PDF ingestion using existing working stack."""

import os, sys, logging
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# Setup paths and load environment
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")
sys.path.append(str(project_root))

import PyPDF2
from src.services.retrieval.retrieval import SemanticRetriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """Optimized PDF processing using existing components."""
    
    def __init__(self, chunk_size: int = 800, overlap: int = 150):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.retriever = SemanticRetriever()
        
    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        logger.info(f"Extracted {len(text)} characters from {os.path.basename(pdf_path)}")
        return text.strip()
    
    def chunk_text(self, text: str, filename: str) -> List[Dict]:
        """Split text into overlapping chunks."""
        if not text.strip():
            return []
        
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words).strip()
            
            if len(chunk_text) > 50:
                chunks.append({
                    "content": chunk_text,
                    "metadata": {
                        "source": filename,
                        "chunk_index": len(chunks),
                        "word_count": len(chunk_words),
                        "type": "pdf_chunk"
                    }
                })
        
        logger.info(f"Created {len(chunks)} chunks from {filename}")
        return chunks
    
    def process_pdf_file(self, pdf_path: str) -> int:
        """Process single PDF file and store chunks."""
        filename = os.path.basename(pdf_path)
        logger.info(f"Processing {filename}...")
        
        try:
            text = self.extract_pdf_text(pdf_path)
            if not text:
                return 0
            
            chunks = self.chunk_text(text, filename)
            if not chunks:
                return 0
            
            stored_count = 0
            for chunk in chunks:
                try:
                    if self.retriever.insert_document(chunk["content"], chunk["metadata"]):
                        stored_count += 1
                except Exception as e:
                    logger.error(f"Failed to store chunk: {e}")
            
            logger.info(f"✅ {filename}: {stored_count}/{len(chunks)} chunks stored")
            return stored_count
            
        except Exception as e:
            logger.error(f"❌ Failed to process {filename}: {e}")
            return 0
    
    def process_data_folder(self, data_dir: str = "data") -> Dict[str, int]:
        """Process all PDF files in data directory."""
        data_path = Path(data_dir)
        if not data_path.exists():
            logger.error(f"Data directory {data_dir} not found")
            return {}
        
        pdf_files = list(data_path.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {data_dir}")
            return {}
        
        results = {}
        total_chunks = 0
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            chunks_stored = self.process_pdf_file(str(pdf_file))
            results[pdf_file.name] = chunks_stored
            total_chunks += chunks_stored
        
        logger.info(f"Processing complete: {total_chunks} total chunks stored")
        return results


def main():
    """Run PDF ingestion process."""
    print("🔄 Starting PDF Data Ingestion...")
    
    try:
        processor = PDFProcessor(chunk_size=800, overlap=150)
        
        # Check vector store connection
        stats = processor.retriever.get_stats()
        if "error" in stats:
            print(f"❌ Vector store error: {stats['error']}")
            return
        
        print(f"✅ Connected to AstraDB: {stats['collection_name']} ({stats['document_count']} docs)")
        
        # Process PDFs
        results = processor.process_data_folder("data")
        
        if results:
            total = sum(results.values())
            successful = len([v for v in results.values() if v > 0])
            print(f"\n🎯 Results: {successful}/{len(results)} files processed, {total} chunks stored")
            
            for filename, count in results.items():
                status = "✅" if count > 0 else "❌"
                print(f"   {status} {filename}: {count} chunks")
        else:
            print("❌ No PDF files processed")
            
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        logger.error(f"Main process error: {e}")


if __name__ == "__main__":
    main()
