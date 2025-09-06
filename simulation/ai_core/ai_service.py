"""
Main AI Service for Clinical AI ExamPro

This service coordinates all AI agents and provides the main interface
for the Django application to interact with the AI system.
"""

import uuid
import json
from typing import Dict, Any, Optional, Tuple
from django.contrib.auth.models import User

from .patient_agent import PatientAgent
from .examiner_workflow import ExaminerWorkflow
from .feedback_agent import FeedbackAgent
from .config import ai_config

class AIService:
    """Main AI service that coordinates all AI agents"""
    
    def __init__(self):
        self.active_sessions = {}  # Store active sessions in memory
        self.llm = ai_config.get_llm()
    
    def start_session(self, user: User, case_data) -> str:
        """
        Start a new AI session
        
        Args:
            user: Django user object
            case_data: Case data from the database
            
        Returns:
            Session ID for the new session
        """
        session_id = str(uuid.uuid4())
        
        # Create patient agent
        patient_agent = PatientAgent(
            case_instructions=case_data.get('instructions_for_patient', '') or '',
            session_id=session_id
        )
        
        # Create examiner workflow
        examiner_workflow = ExaminerWorkflow(case_data)
        
        # Store session data
        session_data = {
            'user': user,
            'case_data': case_data,
            'patient_agent': patient_agent,
            'examiner_workflow': examiner_workflow,
            'session_id': session_id,
            'is_active': True
        }
        
        self.active_sessions[session_id] = session_data
        
        return session_id
    
    def process_user_input(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        Process user input and return appropriate response
        
        Args:
            session_id: Session identifier
            user_input: User's input text
            
        Returns:
            Dictionary containing response data
        """
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        session_data = self.active_sessions[session_id]
        patient_agent = session_data['patient_agent']
        examiner_workflow = session_data['examiner_workflow']
        
        # Process input through patient agent
        is_examiner_request, patient_response = patient_agent.process_user_input(user_input)
        
        if is_examiner_request:
            # Handle examiner request
            examiner_response = examiner_workflow.process_examiner_request(user_input)
            
            return {
                'type': 'examiner_response',
                'response': examiner_response,
                'patient_paused': True
            }
        else:
            # Return patient response
            return {
                'type': 'patient_response',
                'response': patient_response,
                'patient_paused': False
            }
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a session and generate feedback
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing session summary and feedback
        """
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        session_data = self.active_sessions[session_id]
        patient_agent = session_data['patient_agent']
        case_data = session_data['case_data']
        
        # Get conversation transcript
        transcript = patient_agent.memory.get_conversation_string()
        
        # Generate feedback
        feedback_agent = FeedbackAgent(case_data)
        feedback = feedback_agent.generate_feedback(transcript, case_data['case_id'])
        
        # Mark session as inactive
        session_data['is_active'] = False
        
        return {
            'session_id': session_id,
            'transcript': transcript,
            'feedback': feedback,
            'session_ended': True
        }
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get current session state"""
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        session_data = self.active_sessions[session_id]
        patient_agent = session_data['patient_agent']
        
        return {
            'session_id': session_id,
            'is_active': session_data['is_active'],
            'patient_state': patient_agent.get_session_state(),
            'case_id': session_data['case_data']['case_id']
        }
    
    def resume_patient(self, session_id: str) -> bool:
        """Resume patient agent after examiner interaction"""
        if session_id not in self.active_sessions:
            return False
        
        session_data = self.active_sessions[session_id]
        patient_agent = session_data['patient_agent']
        patient_agent.resume_after_examiner()
        
        return True
    
    def clear_session(self, session_id: str) -> bool:
        """Clear session data from memory"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False

# Global AI service instance
ai_service = AIService()
