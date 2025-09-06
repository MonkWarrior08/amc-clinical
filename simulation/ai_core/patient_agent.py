"""
AI Patient Agent for Clinical AI ExamPro

This agent role-plays as the patient based on case instructions and maintains
conversation context throughout the session.
"""

import re
from typing import Dict, Any, Optional, Tuple
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from .config import ai_config
from .memory import SessionMemory

class PatientAgent:
    """AI Patient Agent that role-plays as the patient"""
    
    def __init__(self, case_instructions: str, session_id: str):
        """
        Initialize the Patient Agent
        
        Args:
            case_instructions: Instructions for the patient from the case
            session_id: Unique session identifier
        """
        self.case_instructions = case_instructions
        self.session_id = session_id
        self.memory = SessionMemory(k=15)  # Keep last 15 turns
        self.llm = ai_config.get_llm(temperature=0.8)  # Higher temperature for more natural responses
        self.is_paused = False
        
        # Initialize the patient persona
        self._setup_patient_persona()
    
    def _setup_patient_persona(self):
        """Setup the patient persona based on case instructions"""
        self.persona_prompt = f"""
You are role-playing as a patient in a medical simulation. You must strictly adhere to the following instructions and persona:

{self.case_instructions}

IMPORTANT GUIDELINES:
1. Stay completely in character as the patient described above
2. Only respond based on the information provided in your persona
3. Be empathetic and realistic in your responses
4. Do not generate new medical information not present in your persona
5. If asked about something not in your persona, respond as the patient would (e.g., "I don't know" or "I'm not sure")
6. Maintain consistency with your emotional state and background
7. Respond naturally and conversationally
8. Do not break character or mention that you are an AI

Remember: You are the patient, not a medical professional. Respond only from the patient's perspective.
"""
    
    def detect_examiner_keyword(self, user_input: str) -> bool:
        """
        Detect if the user is addressing the examiner
        
        Args:
            user_input: The user's input text
            
        Returns:
            True if "Examiner" is detected at the beginning
        """
        # Check if input starts with "Examiner" (case insensitive)
        return re.match(r'^\s*examiner\b', user_input, re.IGNORECASE) is not None
    
    def process_user_input(self, user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Process user input and generate patient response
        
        Args:
            user_input: The user's input text
            
        Returns:
            Tuple of (is_examiner_request, patient_response)
            - is_examiner_request: True if user addressed examiner
            - patient_response: Patient's response or None if examiner request
        """
        # Check for examiner keyword
        if self.detect_examiner_keyword(user_input):
            self.is_paused = True
            return True, None
        
        # If previously paused and still examiner request, stay paused
        if self.is_paused and self.detect_examiner_keyword(user_input):
            return True, None
        
        # If previously paused but no examiner keyword, resume
        if self.is_paused and not self.detect_examiner_keyword(user_input):
            self.is_paused = False
        
        # Generate patient response
        patient_response = self._generate_patient_response(user_input)
        
        # Add to memory
        self.memory.add_human_message(user_input)
        self.memory.add_ai_message(patient_response)
        
        return False, patient_response
    
    def _generate_patient_response(self, user_input: str) -> str:
        """Generate patient response using LLM"""
        try:
            # Get conversation history
            conversation_history = self.memory.get_conversation_string()
            
            # Create the prompt
            prompt = f"""
{self.persona_prompt}

CONVERSATION HISTORY:
{conversation_history}

DOCTOR: {user_input}

PATIENT:"""
            
            # Generate response
            response = self.llm.invoke(prompt)
            
            # Extract just the patient's response (remove any extra text)
            patient_response = response.content.strip()
            
            # Clean up the response
            patient_response = self._clean_response(patient_response)
            
            return patient_response
            
        except Exception as e:
            print(f"Error generating patient response: {e}")
            return "I'm sorry, I'm having trouble understanding. Could you please repeat that?"
    
    def _clean_response(self, response: str) -> str:
        """Clean up the AI response to make it more natural"""
        # Remove any prefixes like "PATIENT:" or "Patient:"
        response = re.sub(r'^(PATIENT|Patient):\s*', '', response, flags=re.IGNORECASE)
        
        # Remove any AI-related disclaimers
        response = re.sub(r'\s*\(Note:.*?\)', '', response)
        response = re.sub(r'\s*\[.*?\]', '', response)
        
        # Ensure response ends with proper punctuation
        if response and not response.endswith(('.', '!', '?')):
            response += '.'
        
        return response.strip()
    
    def resume_after_examiner(self):
        """Resume patient role after examiner interaction"""
        self.is_paused = False
    
    def get_session_state(self) -> Dict[str, Any]:
        """Get current session state"""
        return {
            'is_paused': self.is_paused,
            'conversation_turns': len(self.memory.get_messages()),
            'session_id': self.session_id
        }
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        self.is_paused = False
