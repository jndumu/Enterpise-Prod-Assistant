# Data Ingestion System Guide

## Overview

This data ingestion system can read any file type from the `data` folder, chunk the content, create embeddings, and ingest it into AstraDB. It supports multiple file formats and provides a complete pipeline for document processing.

## Supported File Types

| File Type | Extension | Description |
|-----------|-----------|-------------|
| PDF | .pdf | Extracts text from PDF documents |
| Word | .docx | Microsoft Word documents |
| Text | .txt | Plain text files |
| CSV | .csv | Comma-separated values |
| Excel | .xlsx | Microsoft Excel files |
| JSON | .json | JSON data files |
| HTML | .html, .htm | Web pages |
| Markdown | .md | Markdown documents |
| XML | .xml | XML documents |

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your credentials:

```bash
cp env.example .env
```

Edit `.env` file with your credentials:

```env
# Google AI API Key for embeddings
GOOGLE_API_KEY=your_google_api_key_here

# AstraDB Configuration
ASTRA_DB_TOKEN=your_astra_db_token_here
ASTRA_DB_API_ENDPOINT=your_astra_db_api_endpoint_here
```

### 3. Add Files to Data Folder

Place your files in the `data` folder. The system will automatically detect and process all supported file types.

## Usage

### Basic Usage

Run the data ingestion pipeline:

```bash
python src/etl/data_ingestion.py
```

### Test the System

Use the test script to verify everything is working:

```bash
python test_data_ingestion.py
```

### Programmatic Usage

```python
from src.etl.data_ingestion import DataIngestionPipeline

# Initialize pipeline
pipeline = DataIngestionPipeline(
    data_folder="data",
    chunk_size=1000,
    chunk_overlap=200
)

# Process all files
results = pipeline.process_all_files()

print(f"Processed {results['successful']} files successfully")
```

## Configuration

### Chunking Parameters

- `chunk_size`: Maximum characters per chunk (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)

### Embedding Model

The system uses Google's `text-embedding-004` model for generating embeddings. This is configured in `config/config.yaml`.

### AstraDB Collection

Data is stored in the collection specified in `config/config.yaml` under `astra_db.collection_name`.

## File Processing Pipeline

1. **File Detection**: Automatically detects supported file types by extension
2. **Content Extraction**: Extracts text content using appropriate parsers
3. **Text Chunking**: Splits content into manageable chunks with overlap
4. **Embedding Generation**: Creates embeddings using Google's embedding model
5. **Database Storage**: Stores chunks with embeddings and metadata in AstraDB

## Data Structure in AstraDB

Each document stored in AstraDB contains:

```json
{
  "_id": "chunk_0_filename.txt",
  "text": "Chunk content...",
  "embedding": [0.1, 0.2, ...],
  "metadata": {
    "file_name": "filename.txt",
    "file_path": "data/filename.txt",
    "file_size": 1024,
    "file_type": ".txt",
    "chunk_index": 0,
    "start_char": 0,
    "end_char": 1000,
    "chunk_size": 1000
  }
}
```

## Error Handling

The system includes comprehensive error handling:

- **File Reading Errors**: Logged and skipped
- **Encoding Detection**: Automatic encoding detection for text files
- **Embedding Generation Errors**: Logged with fallback
- **Database Errors**: Transaction rollback and error reporting

## Logging

The system provides detailed logging for:
- File processing status
- Chunking information
- Embedding generation progress
- Database operations
- Error messages and warnings

## Performance Considerations

- **Batch Processing**: Documents are inserted in batches of 100
- **Progress Tracking**: Uses tqdm for progress bars
- **Memory Management**: Processes files one at a time
- **Error Recovery**: Continues processing even if individual files fail

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   - Ensure all required environment variables are set
   - Check `.env` file exists and is properly formatted

2. **File Reading Errors**
   - Check file permissions
   - Verify file is not corrupted
   - Ensure file type is supported

3. **Embedding Generation Errors**
   - Verify Google API key is valid
   - Check API quota and limits
   - Ensure internet connectivity

4. **AstraDB Connection Issues**
   - Verify AstraDB credentials
   - Check network connectivity
   - Ensure collection exists

### Debug Mode

Enable debug logging by modifying the logging level in the script:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Example Files

The system includes sample files in the `data` folder:
- `sample_document.txt` - Text document example
- `sample_data.csv` - CSV data example

## Advanced Usage

### Custom File Processors

You can extend the system by adding custom file processors:

```python
class CustomFileProcessor(FileProcessor):
    def _read_custom_format(self, file_path: str) -> str:
        # Custom file reading logic
        pass
```

### Custom Chunking Strategies

Implement custom chunking logic:

```python
class CustomChunker(TextChunker):
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # Custom chunking logic
        pass
```

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify environment configuration
3. Test with sample files first
4. Check file permissions and formats
