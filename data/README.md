# Data Folder

This folder is where you should place files that you want to process and ingest into AstraDB.

## Supported File Types

The data ingestion system supports the following file types:

- **PDF** (.pdf) - Extracts text from PDF documents
- **Word Documents** (.docx) - Extracts text from Microsoft Word documents
- **Text Files** (.txt) - Plain text files
- **CSV Files** (.csv) - Comma-separated values, converted to readable text
- **Excel Files** (.xlsx) - Microsoft Excel files, all sheets processed
- **JSON Files** (.json) - JSON data files, formatted as readable text
- **HTML Files** (.html, .htm) - Web pages, text content extracted
- **Markdown Files** (.md) - Markdown documents, converted to plain text
- **XML Files** (.xml) - XML documents, text content extracted

## Usage

1. Place your files in this `data` folder
2. Run the data ingestion script: `python src/etl/data_ingestion.py`
3. The system will automatically detect, process, and ingest all supported files

## File Processing

- Files are automatically detected by extension
- Text is extracted and chunked for optimal embedding generation
- Embeddings are generated using Google's text-embedding-004 model
- Data is stored in AstraDB with metadata for retrieval

## Configuration

Make sure to set up your environment variables:
- `GOOGLE_API_KEY` - For embedding generation
- `ASTRA_DB_TOKEN` - For AstraDB access
- `ASTRA_DB_API_ENDPOINT` - Your AstraDB endpoint

Copy `env.example` to `.env` and fill in your credentials.
