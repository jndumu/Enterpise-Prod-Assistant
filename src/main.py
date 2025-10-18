"""Optimized PDF ingestion application."""

from etl.data_ingestion import PDFProcessor


def main():
    """Run PDF ingestion pipeline."""
    processor = PDFProcessor()
    
    # Check database connection
    stats = processor.retriever.get_stats()
    if "error" in stats:
        print(f"❌ Database error: {stats['error']}")
        return
    
    print(f"✅ Connected: {stats['collection_name']} ({stats['document_count']} docs)")
    
    # Process files
    results = processor.process_data_folder("data")
    
    if results:
        total = sum(results.values())
        successful = len([v for v in results.values() if v > 0])
        print(f"🎯 {successful}/{len(results)} files, {total} chunks stored")
    else:
        print("❌ No files processed")


if __name__ == "__main__":
    main()
