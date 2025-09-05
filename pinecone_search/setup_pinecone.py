#!/usr/bin/env python3
"""
Setup script for Pinecone PDF processing

This script helps set up the environment and test the Pinecone connection.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["PINECONE_API_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables or create a .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True

def check_pdf_folder():
    """Check if source_pdf folder exists and has PDFs"""
    pdf_folder = Path("../source_info/pdfs")
    
    if not pdf_folder.exists():
        print("❌ source_info/pdfs folder not found")
        return False
    
    pdf_files = list(pdf_folder.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found in source_info/pdfs folder")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"   - {pdf_file.name}")
    
    return True

def test_pinecone_connection():
    """Test Pinecone connection"""
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        
        # List indexes
        indexes = pc.list_indexes()
        print(f"✅ Pinecone connection successful")
        print(f"   Available indexes: {[idx.name for idx in indexes]}")
        
        return True
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI connection"""
    try:
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test with a simple embedding
        test_embedding = embeddings.embed_query("test")
        print(f"✅ OpenAI connection successful")
        print(f"   Embedding dimension: {len(test_embedding)}")
        
        return True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Pinecone PDF Processing Setup")
    print("=" * 40)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    env_ok = check_environment()
    
    # Check PDF folder
    print("\n2. Checking PDF folder...")
    pdf_ok = check_pdf_folder()
    
    if not env_ok or not pdf_ok:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)
    
    # Test connections
    print("\n3. Testing Pinecone connection...")
    pinecone_ok = test_pinecone_connection()
    
    print("\n4. Testing OpenAI connection...")
    openai_ok = test_openai_connection()
    
    if not pinecone_ok or not openai_ok:
        print("\n❌ Connection tests failed. Please check your API keys.")
        sys.exit(1)
    
    print("\n✅ Setup complete! You can now run:")
    print("   python pdf_to_pinecone.py")
    print("   python search_pinecone.py 'your search query'")

if __name__ == "__main__":
    main()
