# PDF to Pinecone Embeddings

This module processes PDF files from the `source_pdf` folder, extracts text, generates embeddings using OpenAI, and uploads them to Pinecone vector database for semantic search.

## Files

- `pdf_to_pinecone.py` - Main script to process PDFs and upload to Pinecone
- `search_pinecone.py` - Interactive search interface for the Pinecone database
- `setup_pinecone.py` - Setup and connection testing script
- `requirements_pinecone.txt` - Additional Python dependencies
- `.env.example` - Environment variables template

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements_pinecone.txt
```

### 2. Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required
export PINECONE_API_KEY="your_pinecone_api_key"
export OPENAI_API_KEY="your_openai_api_key"

# Optional
export PINECONE_INDEX_NAME="medical-cases"
```

### 3. Test Setup

```bash
python setup_pinecone.py
```

## Usage

### Process PDFs and Upload to Pinecone

```bash
python pdf_to_pinecone.py
```

This will:
1. Extract text from all PDFs in `source_pdf/` folder
2. Split text into chunks (1000 chars with 200 char overlap)
3. Generate embeddings using OpenAI
4. Upload to Pinecone index "medical-cases"
5. Test search functionality

### Search the Database

```bash
# Basic search
python search_pinecone.py "medical diagnosis treatment"

# Search with custom number of results
python search_pinecone.py "cardiovascular disease" 10
```

### Programmatic Usage

```python
from pdf_to_pinecone import PDFToPineconeUploader
from search_pinecone import PineconeSearcher

# Upload PDFs
uploader = PDFToPineconeUploader()
documents = uploader.process_all_pdfs()
uploader.upload_to_pinecone(documents)

# Search
searcher = PineconeSearcher()
results = searcher.search("your query", k=5)
```

## Features

- **PDF Text Extraction**: Uses PyPDF for reliable text extraction
- **Text Chunking**: Splits large documents into manageable chunks
- **OpenAI Embeddings**: Uses OpenAI's text-embedding-ada-002 model
- **Pinecone Integration**: Stores vectors in Pinecone for fast similarity search
- **Metadata Preservation**: Maintains file source, chunk information, and other metadata
- **Error Handling**: Robust error handling and logging
- **Search Interface**: Easy-to-use search functionality

## Database Schema

The Pinecone index stores vectors with the following metadata:

```json
{
  "source": "source_pdf/filename.pdf",
  "filename": "filename.pdf",
  "file_type": "pdf",
  "total_chars": 12345,
  "chunk_id": "uuid4",
  "chunk_index": 0,
  "total_chunks": 10
}
```

## Configuration

### Text Splitting
- Chunk size: 1000 characters
- Overlap: 200 characters
- Separators: `["\n\n", "\n", " ", ""]`

### Embeddings
- Model: OpenAI text-embedding-ada-002
- Dimension: 1536
- Similarity metric: Cosine

### Pinecone Index
- Name: "medical-cases" (configurable)
- Cloud: AWS
- Region: us-east-1
- Type: Serverless

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `PINECONE_API_KEY` and `OPENAI_API_KEY` are set
   - Check API key validity

2. **PDF Processing Errors**
   - Ensure PDFs are not password-protected
   - Check file permissions

3. **Pinecone Connection Issues**
   - Verify Pinecone API key
   - Check internet connection
   - Ensure index exists or can be created

4. **Memory Issues with Large PDFs**
   - Reduce chunk size in `RecursiveCharacterTextSplitter`
   - Process PDFs individually

### Logs

The scripts use Python logging. Set log level to DEBUG for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Example Workflow

1. Place PDF files in `source_pdf/` folder
2. Set up environment variables
3. Run setup test: `python setup_pinecone.py`
4. Process and upload: `python pdf_to_pinecone.py`
5. Search: `python search_pinecone.py "your query"`

## Integration with Medical Cases Database

This Pinecone database complements the SQLite medical cases database:

- **SQLite**: Structured case data with categories, sections, and subsections
- **Pinecone**: Semantic search across PDF documents for research and reference

Both can be used together for comprehensive medical case management and research.
