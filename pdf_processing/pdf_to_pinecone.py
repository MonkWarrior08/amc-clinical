#!/usr/bin/env python3
"""
PDF to Pinecone Embeddings Uploader

This script processes PDF files from the source_pdf folder, extracts text,
generates embeddings, and uploads them to Pinecone vector database.
"""

import os
import sys
import uuid
from pathlib import Path
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PDF processing
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Embeddings and Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFToPineconeUploader:
    def __init__(self, 
                 pinecone_api_key: str = None,
                 pinecone_environment: str = None,
                 index_name: str = "amc-tutor",
                 openai_api_key: str = None):
        """
        Initialize the PDF to Pinecone uploader
        
        Args:
            pinecone_api_key: Pinecone API key (if None, will try to get from env)
            pinecone_environment: Pinecone environment (if None, will try to get from env)
            index_name: Name of the Pinecone index
            openai_api_key: OpenAI API key for embeddings (if None, will try to get from env)
        """
        self.index_name = index_name
        self.source_folder = Path("../source_info/pdfs")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=pinecone_api_key or os.getenv("PINECONE_API_KEY"))
        
        # Initialize embeddings (using text-embedding-3-small for 512 dimensions)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key or os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small",
            dimensions=512
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from a PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def process_pdf(self, pdf_path: Path) -> List[Document]:
        """Process a single PDF file and return list of Document objects"""
        logger.info(f"Processing PDF: {pdf_path.name}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text.strip():
            logger.warning(f"No text extracted from {pdf_path.name}")
            return []
        
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
        chunks = self.text_splitter.split_documents([doc])
        
        # Add chunk-specific metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": str(uuid.uuid4()),
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
        
        logger.info(f"Created {len(chunks)} chunks from {pdf_path.name}")
        return chunks
    
    def create_or_get_index(self):
        """Create or get the Pinecone index"""
        try:
            # Check if index exists
            if self.index_name in self.pc.list_indexes().names():
                logger.info(f"Index '{self.index_name}' already exists")
                return self.pc.Index(self.index_name)
            else:
                # Index doesn't exist, but we'll use the existing one
                logger.info(f"Using existing index: {self.index_name}")
                return self.pc.Index(self.index_name)
        except Exception as e:
            logger.error(f"Error creating/getting index: {e}")
            raise
    
    def upload_to_pinecone(self, documents: List[Document]):
        """Upload documents to Pinecone"""
        try:
            # Get or create index
            index = self.create_or_get_index()
            
            # Create vector store
            vectorstore = PineconeVectorStore(
                index=index,
                embedding=self.embeddings
            )
            
            # Upload documents
            logger.info(f"Uploading {len(documents)} documents to Pinecone...")
            vectorstore.add_documents(documents)
            logger.info("Upload completed successfully!")
            
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error uploading to Pinecone: {e}")
            raise
    
    def process_all_pdfs(self) -> List[Document]:
        """Process all PDF files in the source folder"""
        if not self.source_folder.exists():
            logger.error(f"Source folder {self.source_folder} does not exist")
            return []
        
        all_documents = []
        pdf_files = list(self.source_folder.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {self.source_folder}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_path in pdf_files:
            try:
                documents = self.process_pdf(pdf_path)
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                continue
        
        logger.info(f"Total documents processed: {len(all_documents)}")
        return all_documents
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents in Pinecone"""
        try:
            index = self.pc.Index(self.index_name)
            vectorstore = PineconeVectorStore(
                index=index,
                embedding=self.embeddings
            )
            
            results = vectorstore.similarity_search(query, k=k)
            return results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

def main():
    """Main function to process PDFs and upload to Pinecone"""
    # Check for required environment variables
    if not os.getenv("PINECONE_API_KEY"):
        logger.error("PINECONE_API_KEY environment variable not set")
        sys.exit(1)
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize uploader
    uploader = PDFToPineconeUploader()
    
    try:
        # Process all PDFs
        logger.info("Starting PDF processing...")
        documents = uploader.process_all_pdfs()
        
        if not documents:
            logger.error("No documents to upload")
            sys.exit(1)
        
        # Upload to Pinecone
        logger.info("Starting upload to Pinecone...")
        vectorstore = uploader.upload_to_pinecone(documents)
        
        # Test search
        logger.info("Testing search functionality...")
        test_query = "medical diagnosis treatment"
        results = uploader.search_documents(test_query, k=3)
        
        logger.info(f"Search test results for '{test_query}':")
        for i, result in enumerate(results, 1):
            logger.info(f"  {i}. {result.metadata.get('filename', 'Unknown')} - {result.page_content[:100]}...")
        
        logger.info("PDF to Pinecone upload completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
