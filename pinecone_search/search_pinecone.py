#!/usr/bin/env python3
"""
Pinecone Search Interface

This script provides an interactive interface to search the medical documents
stored in Pinecone vector database.
"""

import os
import sys
from typing import List, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PineconeSearcher:
    def __init__(self, 
                 pinecone_api_key: str = None,
                 index_name: str = "amc-tutor",
                 openai_api_key: str = None):
        """
        Initialize the Pinecone searcher
        
        Args:
            pinecone_api_key: Pinecone API key
            index_name: Name of the Pinecone index
            openai_api_key: OpenAI API key for embeddings
        """
        self.index_name = index_name
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=pinecone_api_key or os.getenv("PINECONE_API_KEY"))
        
        # Initialize embeddings (using text-embedding-3-small for 512 dimensions)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key or os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small",
            dimensions=512
        )
        
        # Initialize vector store
        self.index = self.pc.Index(self.index_name)
        self.vectorstore = PineconeVectorStore(
            index=self.index,
            embedding=self.embeddings
        )
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def search_with_scores(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents with similarity scores"""
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Error searching with scores: {e}")
            return []
    
    def get_index_stats(self) -> Dict:
        """Get index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}

def main():
    """Interactive search interface"""
    if len(sys.argv) < 2:
        print("Usage: python search_pinecone.py <query> [k]")
        print("  query: Search query")
        print("  k: Number of results to return (default: 5)")
        return
    
    # Check for required environment variables
    if not os.getenv("PINECONE_API_KEY"):
        logger.error("PINECONE_API_KEY environment variable not set")
        sys.exit(1)
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    query = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    try:
        # Initialize searcher
        searcher = PineconeSearcher()
        
        # Get index stats
        stats = searcher.get_index_stats()
        if stats:
            print(f"Index: {searcher.index_name}")
            print(f"Total vectors: {stats.get('total_vector_count', 'Unknown')}")
            print()
        
        # Search
        print(f"Searching for: '{query}'")
        print(f"Number of results: {k}")
        print("=" * 60)
        
        results = searcher.search_with_scores(query, k)
        
        if not results:
            print("No results found.")
            return
        
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n{i}. Score: {score:.4f}")
            print(f"   File: {doc.metadata.get('filename', 'Unknown')}")
            print(f"   Chunk: {doc.metadata.get('chunk_index', 'N/A')}/{doc.metadata.get('total_chunks', 'N/A')}")
            print(f"   Content: {doc.page_content[:200]}...")
            print("-" * 40)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
