# AMC Clinical - Medical Cases Management System

A comprehensive system for managing medical cases with both structured database storage and semantic search capabilities.

## 📁 Project Structure

```
amc-clinical/
├── database/                    # SQLite database management
│   ├── create_medical_cases_db.py
│   ├── test_database.py
│   ├── query_database.py
│   └── medical_cases.db
├── pdf_processing/              # PDF text extraction and processing
│   ├── pdf_to_pinecone.py
│   └── test_pdf_processing.py
├── pinecone_search/            # Pinecone vector search
│   ├── search_pinecone.py
│   └── setup_pinecone.py
├── scripts/                    # Utility scripts
│   └── requirements_pinecone.txt
├── docs/                       # Documentation
│   └── README_PINECONE.md
├── source_info/                # Source data files
│   ├── cases/                  # Medical cases text files
│   │   ├── cases.txt
│   │   └── cases2.txt
│   └── pdfs/                   # PDF documents
│       ├── management_print.pdf
│       ├── chapter 3 and 4_print.pdf
│       ├── Master medcine 2_print.pdf
│       └── medicine 1_print.pdf
├── core/                       # Django core
├── simulation/                 # Django simulation app
├── cases.txt                   # Medical cases data
├── cases2.txt                  # Additional medical cases data
└── .env                        # Environment variables
```

## 🚀 Quick Start

### 1. Database Management (SQLite)

```bash
# Create and populate the medical cases database
cd database
python create_medical_cases_db.py

# Test the database
python test_database.py

# Query the database
python query_database.py categories
python query_database.py cases Cardiovascular_system
python query_database.py case Erin_Campbell
```

### 2. PDF Processing and Pinecone Upload

```bash
# Set up environment variables
export PINECONE_API_KEY="your_pinecone_api_key"
export OPENAI_API_KEY="your_openai_api_key"

# Test PDF processing
cd pdf_processing
python test_pdf_processing.py

# Upload PDFs to Pinecone
python pdf_to_pinecone.py
```

### 3. Semantic Search

```bash
# Test Pinecone setup
cd pinecone_search
python setup_pinecone.py

# Search the vector database
python search_pinecone.py "medical diagnosis treatment"
python search_pinecone.py "cardiovascular disease" 10
```

## 📊 Database Statistics

- **Medical Cases**: 50 cases across 15 categories
- **Sections**: 181 structured sections
- **Subsections**: 371 detailed subsections
- **PDF Chunks**: 2,424 searchable text chunks
- **Total PDF Content**: 1.5M+ characters

## 🔧 Features

### SQLite Database
- Structured medical case data
- Categories, sections, and subsections
- Easy querying and filtering
- Relational data integrity

### Pinecone Vector Search
- Semantic search across PDF documents
- OpenAI embeddings (text-embedding-3-small)
- 512-dimensional vectors
- Cosine similarity matching

### PDF Processing
- Text extraction from PDFs
- Smart chunking (1000 chars, 200 overlap)
- Metadata preservation
- Error handling and logging

## 📚 Documentation

- [Pinecone Integration Guide](docs/README_PINECONE.md)
- [Database Schema](database/)
- [PDF Processing](pdf_processing/)
- [Search Interface](pinecone_search/)

## 🛠️ Installation

```bash
# Install base requirements
pip install -r requirements.txt

# Install Pinecone requirements
pip install -r scripts/requirements_pinecone.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

## 🔍 Usage Examples

### Search Medical Cases
```bash
# Find all cardiovascular cases
python database/query_database.py cases Cardiovascular_system

# Get detailed case information
python database/query_database.py case Dilip_Patel
```

### Search PDF Content
```bash
# Search for treatment information
python pinecone_search/search_pinecone.py "treatment plan management"

# Search with more results
python pinecone_search/search_pinecone.py "diagnosis" 10
```

## 📈 Data Flow

1. **Text Files** → **SQLite Database** (Structured case data)
2. **PDF Files** → **Text Extraction** → **Chunking** → **Pinecone** (Semantic search)
3. **Queries** → **Both Systems** → **Comprehensive Results**

## 🔑 Environment Variables

```bash
# Required for Pinecone
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional
PINECONE_INDEX_NAME=amc-tutor
```

## 📝 Notes

- The system uses your existing Pinecone index "amc-tutor"
- All PDFs are processed into 2,424 searchable chunks
- Database contains 50 medical cases with full metadata
- Both systems complement each other for comprehensive medical case management
