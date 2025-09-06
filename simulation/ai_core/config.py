"""
Configuration and shared components for AI agents
"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIConfig:
    """Configuration class for AI components"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "amc-tutor")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not self.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
    
    def get_llm(self, model_name: str = "gpt-4", temperature: float = 0.7) -> ChatOpenAI:
        """Get configured OpenAI LLM"""
        return ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model_name=model_name,
            temperature=temperature
        )
    
    def get_embeddings(self) -> OpenAIEmbeddings:
        """Get configured OpenAI embeddings"""
        return OpenAIEmbeddings(
            openai_api_key=self.openai_api_key,
            model="text-embedding-3-small",
            dimensions=512
        )
    
    def get_pinecone_client(self) -> Pinecone:
        """Get Pinecone client"""
        return Pinecone(api_key=self.pinecone_api_key)
    
    def get_vector_store(self) -> PineconeVectorStore:
        """Get Pinecone vector store"""
        pc = self.get_pinecone_client()
        index = pc.Index(self.pinecone_index_name)
        embeddings = self.get_embeddings()
        
        return PineconeVectorStore(
            index=index,
            embedding=embeddings
        )

# Global config instance
ai_config = AIConfig()
