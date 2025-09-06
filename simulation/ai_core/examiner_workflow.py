"""
Examiner Findings Workflow for Clinical AI ExamPro

This module handles the retrieval of examination findings when the user
addresses the "Examiner" during a simulation session.
"""

import re
from typing import Dict, Any, Optional, List
from .config import ai_config

class ExaminerWorkflow:
    """Handles examiner findings retrieval and response generation"""
    
    def __init__(self, case_data):
        """
        Initialize the Examiner Workflow
        
        Args:
            case_data: Case data containing examination details
        """
        self.case_data = case_data
        self.llm = ai_config.get_llm(temperature=0.3)  # Lower temperature for factual responses
    
    def parse_examiner_request(self, user_input: str) -> Dict[str, Any]:
        """
        Parse the examiner request to understand what findings are needed
        
        Args:
            user_input: The user's input starting with "Examiner"
            
        Returns:
            Dictionary containing parsed request information
        """
        # Remove "Examiner" prefix and clean up
        request_text = re.sub(r'^\s*examiner\s*:?\s*', '', user_input, flags=re.IGNORECASE).strip()
        
        # Parse different types of requests
        request_type = self._classify_request(request_text)
        
        return {
            'original_input': user_input,
            'cleaned_request': request_text,
            'request_type': request_type,
            'keywords': self._extract_keywords(request_text)
        }
    
    def _classify_request(self, request_text: str) -> str:
        """Classify the type of examiner request"""
        request_lower = request_text.lower()
        
        # Physical examination requests
        if any(keyword in request_lower for keyword in ['examine', 'look at', 'check', 'inspect', 'observe']):
            return 'physical_exam'
        
        # Lab results requests
        if any(keyword in request_lower for keyword in ['lab', 'blood', 'test', 'result', 'investigation']):
            return 'lab_results'
        
        # Imaging requests
        if any(keyword in request_lower for keyword in ['x-ray', 'ct', 'mri', 'scan', 'imaging']):
            return 'imaging'
        
        # Vital signs requests
        if any(keyword in request_lower for keyword in ['vital', 'blood pressure', 'temperature', 'pulse', 'heart rate']):
            return 'vital_signs'
        
        # General findings request
        if any(keyword in request_lower for keyword in ['findings', 'results', 'what do you see', 'show me']):
            return 'general_findings'
        
        return 'general_findings'
    
    def _extract_keywords(self, request_text: str) -> List[str]:
        """Extract relevant keywords from the request"""
        # Common medical examination keywords
        keywords = []
        
        # Body parts
        body_parts = ['head', 'neck', 'chest', 'abdomen', 'back', 'limbs', 'extremities', 
                     'face', 'eyes', 'ears', 'nose', 'mouth', 'throat', 'heart', 'lungs']
        
        for part in body_parts:
            if part in request_text.lower():
                keywords.append(part)
        
        # Examination types
        exam_types = ['inspection', 'palpation', 'auscultation', 'percussion', 'examination']
        
        for exam_type in exam_types:
            if exam_type in request_text.lower():
                keywords.append(exam_type)
        
        return keywords
    
    def retrieve_findings(self, parsed_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve relevant examination findings based on the request
        
        Args:
            parsed_request: Parsed request information
            
        Returns:
            Dictionary containing retrieved findings
        """
        request_type = parsed_request['request_type']
        
        # Get the appropriate findings based on request type
        if request_type == 'physical_exam':
            findings = self._get_physical_exam_findings(parsed_request)
        elif request_type == 'lab_results':
            findings = self._get_lab_results(parsed_request)
        elif request_type == 'imaging':
            findings = self._get_imaging_findings(parsed_request)
        elif request_type == 'vital_signs':
            findings = self._get_vital_signs(parsed_request)
        else:
            findings = self._get_general_findings(parsed_request)
        
        return {
            'request_type': request_type,
            'findings': findings,
            'source': 'case_data',
            'keywords_used': parsed_request['keywords']
        }
    
    def _get_physical_exam_findings(self, parsed_request: Dict[str, Any]) -> str:
        """Get physical examination findings"""
        # Prioritize facilitator-specific findings if available
        if self.case_data.info_for_facilitator_exam_findings:
            return self.case_data.info_for_facilitator_exam_findings
        
        # Fall back to general examination details
        if self.case_data.examination_details:
            return self.case_data.examination_details
        
        return "No specific physical examination findings available for this case."
    
    def _get_lab_results(self, parsed_request: Dict[str, Any]) -> str:
        """Get laboratory results"""
        # Check for lab results in examination details
        exam_details = self.case_data.examination_details or ''
        info_for_facilitator = self.case_data.info_for_facilitator_exam_findings or ''
        
        # Look for lab-related content
        lab_content = ""
        if 'lab' in info_for_facilitator.lower() or 'blood' in info_for_facilitator.lower():
            lab_content = info_for_facilitator
        elif 'lab' in exam_details.lower() or 'blood' in exam_details.lower():
            lab_content = exam_details
        
        if lab_content:
            return lab_content
        
        return "No laboratory results available for this case."
    
    def _get_imaging_findings(self, parsed_request: Dict[str, Any]) -> str:
        """Get imaging findings"""
        # Check for imaging results in examination details
        exam_details = self.case_data.examination_details or ''
        info_for_facilitator = self.case_data.info_for_facilitator_exam_findings or ''
        
        # Look for imaging-related content
        imaging_content = ""
        if any(keyword in info_for_facilitator.lower() for keyword in ['x-ray', 'ct', 'mri', 'scan', 'imaging']):
            imaging_content = info_for_facilitator
        elif any(keyword in exam_details.lower() for keyword in ['x-ray', 'ct', 'mri', 'scan', 'imaging']):
            imaging_content = exam_details
        
        if imaging_content:
            return imaging_content
        
        return "No imaging results available for this case."
    
    def _get_vital_signs(self, parsed_request: Dict[str, Any]) -> str:
        """Get vital signs"""
        # Check for vital signs in examination details
        exam_details = self.case_data.examination_details or ''
        info_for_facilitator = self.case_data.info_for_facilitator_exam_findings or ''
        
        # Look for vital signs content
        vital_content = ""
        if any(keyword in info_for_facilitator.lower() for keyword in ['blood pressure', 'temperature', 'pulse', 'heart rate', 'vital']):
            vital_content = info_for_facilitator
        elif any(keyword in exam_details.lower() for keyword in ['blood pressure', 'temperature', 'pulse', 'heart rate', 'vital']):
            vital_content = exam_details
        
        if vital_content:
            return vital_content
        
        return "No specific vital signs recorded for this case."
    
    def _get_general_findings(self, parsed_request: Dict[str, Any]) -> str:
        """Get general examination findings"""
        # Prioritize facilitator-specific findings
        if self.case_data.info_for_facilitator_exam_findings:
            return self.case_data.info_for_facilitator_exam_findings
        
        # Fall back to general examination details
        if self.case_data.examination_details:
            return self.case_data.examination_details
        
        return "No examination findings available for this case."
    
    def format_response(self, findings_data: Dict[str, Any]) -> str:
        """
        Format the findings into a readable response
        
        Args:
            findings_data: Retrieved findings data
            
        Returns:
            Formatted response string
        """
        request_type = findings_data['request_type']
        findings = findings_data['findings']
        
        # Create a formatted response
        response = f"**Examiner Findings - {request_type.replace('_', ' ').title()}**\n\n"
        response += findings
        
        # Add source information
        response += f"\n\n*Source: {findings_data['source']}*"
        
        return response
    
    def process_examiner_request(self, user_input: str) -> str:
        """
        Complete workflow for processing an examiner request
        
        Args:
            user_input: The user's input starting with "Examiner"
            
        Returns:
            Formatted response with examination findings
        """
        # Parse the request
        parsed_request = self.parse_examiner_request(user_input)
        
        # Retrieve findings
        findings_data = self.retrieve_findings(parsed_request)
        
        # Format response
        response = self.format_response(findings_data)
        
        return response
