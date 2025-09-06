"""
Memory management for AI agents
"""

from typing import List, Dict, Any
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage

class SessionMemory:
    """Enhanced memory management for AI sessions"""
    
    def __init__(self, k: int = 10):
        """
        Initialize session memory
        
        Args:
            k: Number of conversation turns to keep in memory
        """
        self.memory = ConversationBufferWindowMemory(k=k, return_messages=True)
        self.session_metadata = {}
    
    def add_human_message(self, message: str, metadata: Dict[str, Any] = None):
        """Add a human message to memory"""
        self.memory.chat_memory.add_user_message(message)
        if metadata:
            self.session_metadata[f"human_{len(self.memory.chat_memory.messages)}"] = metadata
    
    def add_ai_message(self, message: str, metadata: Dict[str, Any] = None):
        """Add an AI message to memory"""
        self.memory.chat_memory.add_ai_message(message)
        if metadata:
            self.session_metadata[f"ai_{len(self.memory.chat_memory.messages)}"] = metadata
    
    def get_messages(self) -> List[BaseMessage]:
        """Get all messages from memory"""
        return self.memory.chat_memory.messages
    
    def get_conversation_string(self) -> str:
        """Get conversation as a formatted string"""
        return self.memory.buffer
    
    def clear(self):
        """Clear all memory"""
        self.memory.clear()
        self.session_metadata.clear()
    
    def get_memory_variables(self) -> List[str]:
        """Get memory variables for LangChain"""
        return self.memory.memory_variables
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables"""
        return self.memory.load_memory_variables(inputs)
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]):
        """Save context to memory"""
        self.memory.save_context(inputs, outputs)
