#!/usr/bin/env python3
"""
Test PDF processing without API keys

This script tests the PDF text extraction and chunking functionality
without requiring Pinecone or OpenAI API keys.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# PDF processing
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pdf_processing():
    """Test PDF processing functionality"""
    source_folder = Path("../source_info/pdfs")
    
    if not source_folder.exists():
        logger.error(f"Source folder {source_folder} does not exist")
        return
    
    pdf_files = list(source_folder.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {source_folder}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to test")
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    total_chunks = 0
    total_chars = 0
    
    for pdf_path in pdf_files:
        logger.info(f"\nProcessing: {pdf_path.name}")
        
        try:
            # Extract text
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            if not text.strip():
                logger.warning(f"No text extracted from {pdf_path.name}")
                continue
            
            logger.info(f"Extracted {len(text)} characters")
            total_chars += len(text)
            
            # Create document
            doc = Document(
                page_content=text,
                metadata={
                    "source": str(pdf_path),
                    "filename": pdf_path.name,
                    "file_type": "pdf",
                    "total_chars": len(text)
                }
            )
            
            # Split into chunks
            chunks = text_splitter.split_documents([doc])
            logger.info(f"Created {len(chunks)} chunks")
            total_chunks += len(chunks)
            
            # Show sample chunks
            for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
                logger.info(f"  Chunk {i+1}: {len(chunk.page_content)} chars")
                logger.info(f"    Preview: {chunk.page_content[:100]}...")
            
            if len(chunks) > 2:
                logger.info(f"  ... and {len(chunks) - 2} more chunks")
        
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            continue
    
    logger.info(f"\n=== SUMMARY ===")
    logger.info(f"Total PDFs processed: {len(pdf_files)}")
    logger.info(f"Total characters extracted: {total_chars:,}")
    logger.info(f"Total chunks created: {total_chunks}")
    logger.info(f"Average chars per chunk: {total_chars // total_chunks if total_chunks > 0 else 0}")
    
    # Test search simulation
    logger.info(f"\n=== SEARCH SIMULATION ===")
    sample_queries = [
        "medical diagnosis",
        "treatment plan",
        "cardiovascular",
        "patient care"
    ]
    
    for query in sample_queries:
        logger.info(f"Query: '{query}'")
        # In a real scenario, this would search the vector database
        logger.info("  -> Would search Pinecone vector database for similar content")
        logger.info("  -> Would return ranked results with similarity scores")

if __name__ == "__main__":
    test_pdf_processing()
