"""
Feedback Generation Agent for Clinical AI ExamPro

This agent generates comprehensive feedback reports using RAG (Retrieval-Augmented Generation)
to provide detailed, evidence-based feedback for medical simulation sessions.
"""

import time
import re
from typing import Dict, Any, List, Tuple, Optional
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from .config import ai_config

class FeedbackAgent:
    """AI Feedback Agent that generates comprehensive feedback reports"""
    
    def __init__(self, case_data, vector_store=None):
        """
        Initialize the Feedback Agent
        
        Args:
            case_data: Case data containing suggested approach and evaluation criteria
            vector_store: Pinecone vector store for RAG (optional)
        """
        self.case_data = case_data
        self.vector_store = vector_store or ai_config.get_vector_store()
        self.llm = ai_config.get_llm(temperature=0.3)  # Lower temperature for consistent feedback
        self.rag_queries_used = []
    
    def _get_suggested_approach(self) -> Dict[str, Any]:
        """Support both Case model instances and dict case_data."""
        try:
            # Model-style access
            if hasattr(self.case_data, 'get_suggested_approach'):
                return self.case_data.get_suggested_approach()
        except Exception:
            pass
        # Dict-style fallback
        data = self.case_data if isinstance(self.case_data, dict) else {}
        return {
            'specific_questions': data.get('specific_questions', ''),
            'examination_details': data.get('examination_details', ''),
            'management_plan': data.get('management_plan', ''),
            'case_commentary': data.get('case_commentary', ''),
            'pitfalls': data.get('pitfalls', '')
        }

    def generate_feedback(self, session_transcript: str, case_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive feedback for a session
        
        Args:
            session_transcript: Full transcript of the session
            case_id: ID of the case being practiced
            
        Returns:
            Dictionary containing comprehensive feedback
        """
        start_time = time.time()
        
        # Get suggested approach for evaluation (robust to dict or model instance)
        suggested_approach = self._get_suggested_approach()
        
        # Analyze the session
        analysis = self._analyze_session(session_transcript, suggested_approach)
        
        # Generate RAG-enhanced feedback
        rag_enhanced_feedback = self._generate_rag_enhanced_feedback(
            analysis, suggested_approach, case_id
        )
        
        # Calculate scores
        scores = self._calculate_scores(analysis, suggested_approach)
        
        # Generate final feedback report
        feedback_report = self._generate_final_report(
            analysis, rag_enhanced_feedback, scores, suggested_approach
        )
        
        generation_time = time.time() - start_time
        
        return {
            'overall_score': scores['overall_score'],
            'pass_fail': scores['pass_fail'],
            'coverage_percentage': round(analysis.get('coverage_percentage', 0), 1),
            'covered_count': len(analysis.get('key_points_covered', [])),
            'missed_count': len(analysis.get('key_points_missed', [])),
            'total_key_points': analysis.get('total_key_points', 0),
            'compliance_penalty': scores.get('compliance_penalty', 0),
            'what_went_well': feedback_report['what_went_well'],
            'areas_for_improvement': feedback_report['areas_for_improvement'],
            'specific_recommendations': feedback_report['specific_recommendations'],
            'key_points_covered': analysis['key_points_covered'],
            'key_points_missed': analysis['key_points_missed'],
            'compliance_analysis': analysis['compliance_analysis'],
            'rag_sources': self.rag_queries_used,
            'generation_time_seconds': generation_time
        }
    
    def _analyze_session(self, transcript: str, suggested_approach: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the session against the suggested approach"""
        
        # Extract key points from suggested approach
        key_points = self._extract_key_points(suggested_approach)
        
        # Analyze what was covered
        covered_points = self._analyze_covered_points(transcript, key_points)
        
        # Analyze what was missed
        missed_points = self._analyze_missed_points(transcript, key_points, covered_points)
        
        # Analyze compliance with instructions
        compliance = self._analyze_compliance(transcript, suggested_approach)
        
        return {
            'key_points_covered': covered_points,
            'key_points_missed': missed_points,
            'compliance_analysis': compliance,
            'total_key_points': len(key_points),
            'coverage_percentage': len(covered_points) / len(key_points) * 100 if key_points else 0
        }
    
    def _extract_key_points(self, suggested_approach: Dict[str, Any]) -> List[str]:
        """Extract key points from the suggested approach"""
        key_points = []
        
        # Extract from specific questions
        if suggested_approach.get('specific_questions'):
            questions = self._extract_questions(suggested_approach['specific_questions'])
            key_points.extend(questions)
        
        # Extract from examination details
        if suggested_approach.get('examination_details'):
            exam_points = self._extract_examination_points(suggested_approach['examination_details'])
            key_points.extend(exam_points)
        
        # Extract from management plan
        if suggested_approach.get('management_plan'):
            management_points = self._extract_management_points(suggested_approach['management_plan'])
            key_points.extend(management_points)
        
        # Extract from pitfalls
        if suggested_approach.get('pitfalls'):
            pitfall_points = self._extract_pitfall_points(suggested_approach['pitfalls'])
            key_points.extend(pitfall_points)
        
        return key_points
    
    def _extract_questions(self, questions_text: str) -> List[str]:
        """Extract specific questions from text"""
        # Look for question patterns
        question_patterns = [
            r'[?]',  # Questions ending with ?
            r'ask about',  # "ask about" patterns
            r'inquire about',  # "inquire about" patterns
            r'explore',  # "explore" patterns
        ]
        
        questions = []
        for pattern in question_patterns:
            matches = re.finditer(pattern, questions_text, re.IGNORECASE)
            for match in matches:
                # Extract context around the match
                start = max(0, match.start() - 50)
                end = min(len(questions_text), match.end() + 50)
                context = questions_text[start:end].strip()
                if context not in questions:
                    questions.append(context)
        
        return questions
    
    def _extract_examination_points(self, exam_text: str) -> List[str]:
        """Extract examination points from text"""
        # Look for examination-related patterns
        exam_patterns = [
            r'examine',  # "examine" patterns
            r'check',  # "check" patterns
            r'assess',  # "assess" patterns
            r'evaluate',  # "evaluate" patterns
        ]
        
        points = []
        for pattern in exam_patterns:
            matches = re.finditer(pattern, exam_text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(exam_text), match.end() + 30)
                context = exam_text[start:end].strip()
                if context not in points:
                    points.append(context)
        
        return points
    
    def _extract_management_points(self, management_text: str) -> List[str]:
        """Extract management points from text"""
        # Look for management-related patterns
        management_patterns = [
            r'treat',  # "treat" patterns
            r'manage',  # "manage" patterns
            r'prescribe',  # "prescribe" patterns
            r'refer',  # "refer" patterns
        ]
        
        points = []
        for pattern in management_patterns:
            matches = re.finditer(pattern, management_text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(management_text), match.end() + 30)
                context = management_text[start:end].strip()
                if context not in points:
                    points.append(context)
        
        return points
    
    def _extract_pitfall_points(self, pitfalls_text: str) -> List[str]:
        """Extract pitfall points from text"""
        # Look for pitfall-related patterns
        pitfall_patterns = [
            r'avoid',  # "avoid" patterns
            r'don\'t',  # "don't" patterns
            r'not',  # "not" patterns
            r'warning',  # "warning" patterns
        ]
        
        points = []
        for pattern in pitfall_patterns:
            matches = re.finditer(pattern, pitfalls_text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(pitfalls_text), match.end() + 30)
                context = pitfalls_text[start:end].strip()
                if context not in points:
                    points.append(context)
        
        return points
    
    def _analyze_covered_points(self, transcript: str, key_points: List[str]) -> List[str]:
        """Analyze which key points were covered in the session"""
        covered = []
        
        for point in key_points:
            # Check if the point is mentioned in the transcript
            if self._is_point_covered(transcript, point):
                covered.append(point)
        
        return covered
    
    def _is_point_covered(self, transcript: str, point: str) -> bool:
        """Check if a specific point was covered in the transcript"""
        # Extract keywords from the point
        keywords = self._extract_keywords(point)
        
        # Check if enough keywords are present in the transcript
        keyword_matches = 0
        for keyword in keywords:
            if keyword.lower() in transcript.lower():
                keyword_matches += 1
        
        # Consider covered if at least 50% of keywords are present
        return keyword_matches >= len(keywords) * 0.5
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Remove common words and extract meaningful terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        
        return keywords
    
    def _analyze_missed_points(self, transcript: str, key_points: List[str], covered_points: List[str]) -> List[str]:
        """Analyze which key points were missed"""
        return [point for point in key_points if point not in covered_points]
    
    def _analyze_compliance(self, transcript: str, suggested_approach: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compliance with specific instructions"""
        compliance = {
            'used_jargon': self._check_jargon_usage(transcript),
            'maintained_rapport': self._check_rapport_maintenance(transcript),
            'followed_protocol': self._check_protocol_following(transcript, suggested_approach),
            'addressed_concerns': self._check_concern_addressing(transcript)
        }
        
        return compliance
    
    def _check_jargon_usage(self, transcript: str) -> bool:
        """Check if medical jargon was used inappropriately"""
        # Look for complex medical terms that might be jargon
        jargon_patterns = [
            r'\b(contraindication|contraindicated)\b',
            r'\b(pathophysiology|pathological)\b',
            r'\b(etiology|aetiology)\b',
            r'\b(prognosis|prognostic)\b'
        ]
        
        for pattern in jargon_patterns:
            if re.search(pattern, transcript, re.IGNORECASE):
                return True
        
        return False
    
    def _check_rapport_maintenance(self, transcript: str) -> bool:
        """Check if rapport was maintained"""
        rapport_indicators = [
            r'how are you feeling',
            r'how do you feel',
            r'is there anything else',
            r'do you have any questions',
            r'does that make sense',
            r'are you comfortable'
        ]
        
        for pattern in rapport_indicators:
            if re.search(pattern, transcript, re.IGNORECASE):
                return True
        
        return False
    
    def _check_protocol_following(self, transcript: str, suggested_approach: Dict[str, Any]) -> bool:
        """Check if medical protocol was followed"""
        # This would need to be customized based on specific protocols
        # For now, return True as a placeholder
        return True
    
    def _check_concern_addressing(self, transcript: str) -> bool:
        """Check if patient concerns were addressed"""
        concern_indicators = [
            r'concern',
            r'worried',
            r'anxious',
            r'fear',
            r'worry'
        ]
        
        for pattern in concern_indicators:
            if re.search(pattern, transcript, re.IGNORECASE):
                return True
        
        return False
    
    def _generate_rag_enhanced_feedback(self, analysis: Dict[str, Any], 
                                      suggested_approach: Dict[str, Any], 
                                      case_id: str) -> Dict[str, Any]:
        """Generate RAG-enhanced feedback using Pinecone"""
        rag_enhanced = {
            'what_went_well': [],
            'areas_for_improvement': [],
            'specific_recommendations': []
        }
        
        # Generate queries for areas of improvement
        for missed_point in analysis['key_points_missed']:
            query = self._generate_rag_query(missed_point, case_id)
            if query:
                rag_results = self._query_pinecone(query, case_id)
                if rag_results:
                    rag_enhanced['areas_for_improvement'].extend(rag_results)
        
        # Generate queries for compliance issues
        for compliance_issue, is_violated in analysis['compliance_analysis'].items():
            if is_violated:
                query = self._generate_rag_query(compliance_issue, case_id)
                if query:
                    rag_results = self._query_pinecone(query, case_id)
                    if rag_results:
                        rag_enhanced['specific_recommendations'].extend(rag_results)
        
        return rag_enhanced
    
    def _generate_rag_query(self, topic: str, case_id: str) -> str:
        """Generate a search query for RAG"""
        # Extract key terms from the topic
        keywords = self._extract_keywords(topic)
        
        # Create a focused query
        query = f"medical {topic} best practices guidelines"
        
        # Add case-specific context
        if 'adolescent' in case_id.lower():
            query += " adolescent health"
        elif 'cardiovascular' in case_id.lower():
            query += " cardiovascular medicine"
        elif 'mental' in case_id.lower():
            query += " mental health psychiatry"
        
        return query
    
    def _query_pinecone(self, query: str, case_id: str) -> List[str]:
        """Query Pinecone for relevant information"""
        try:
            # Add category filter based on case
            category_filter = self._get_category_filter(case_id)
            
            # Query with filter
            results = self.vector_store.similarity_search(
                query, 
                k=3,
                filter=category_filter
            )
            
            # Extract relevant content
            relevant_content = []
            for result in results:
                content = result.page_content
                if content and len(content) > 50:  # Filter out very short content
                    relevant_content.append(content)
            
            # Store query for tracking
            self.rag_queries_used.append({
                'query': query,
                'results_count': len(relevant_content),
                'case_id': case_id
            })
            
            return relevant_content
            
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            return []
    
    def _get_category_filter(self, case_id: str) -> Dict[str, str]:
        """Get category filter for Pinecone query"""
        # Map case categories to Pinecone category types
        category_mapping = {
            'adolescent_health': 'Adolescent Health',
            'cardiovascular_system': 'Cardiovascular Medicine',
            'mental_health': 'Mental Health',
            'dermatology': 'Dermatology',
            'emergency_medicine': 'Emergency Medicine'
        }
        
        # Extract category from case_id or use default
        for category, pinecone_category in category_mapping.items():
            if category in case_id.lower():
                return {'category_type': pinecone_category}
        
        return {}
    
    def _calculate_scores(self, analysis: Dict[str, Any], suggested_approach: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate scores for the session"""
        # Base score on coverage percentage
        coverage_score = analysis['coverage_percentage']
        
        # Adjust for compliance
        compliance_penalty = 0
        for issue, is_violated in analysis['compliance_analysis'].items():
            if is_violated:
                compliance_penalty += 10
        
        # Calculate overall score
        overall_score = max(0, coverage_score - compliance_penalty)
        
        # Determine pass/fail (threshold of 70%)
        pass_fail = overall_score >= 70
        
        return {
            'overall_score': round(overall_score, 1),
            'pass_fail': pass_fail,
            'coverage_score': coverage_score,
            'compliance_penalty': compliance_penalty
        }
    
    def _generate_final_report(self, analysis: Dict[str, Any], 
                             rag_enhanced: Dict[str, Any], 
                             scores: Dict[str, Any], 
                             suggested_approach: Dict[str, Any]) -> Dict[str, str]:
        """Generate the final feedback report"""
        
        # Generate what went well
        what_went_well = self._generate_what_went_well(analysis, rag_enhanced)
        
        # Generate areas for improvement
        areas_for_improvement = self._generate_areas_for_improvement(analysis, rag_enhanced)
        
        # Generate specific recommendations
        specific_recommendations = self._generate_specific_recommendations(analysis, rag_enhanced)
        
        return {
            'what_went_well': what_went_well,
            'areas_for_improvement': areas_for_improvement,
            'specific_recommendations': specific_recommendations
        }
    
    def _generate_what_went_well(self, analysis: Dict[str, Any], rag_enhanced: Dict[str, Any]) -> str:
        """Generate what went well section"""
        points = []
        
        # Add covered points
        if analysis['key_points_covered']:
            points.append(f"Successfully addressed {len(analysis['key_points_covered'])} key points from the suggested approach.")
        
        # Add compliance strengths
        compliance_strengths = []
        for issue, is_violated in analysis['compliance_analysis'].items():
            if not is_violated:
                compliance_strengths.append(issue.replace('_', ' ').title())
        
        if compliance_strengths:
            points.append(f"Demonstrated good compliance with: {', '.join(compliance_strengths)}.")
        
        # Add RAG-enhanced points
        if rag_enhanced['what_went_well']:
            points.extend(rag_enhanced['what_went_well'])
        
        return " ".join(points) if points else "No specific strengths identified in this session."
    
    def _generate_areas_for_improvement(self, analysis: Dict[str, Any], rag_enhanced: Dict[str, Any]) -> str:
        """Generate areas for improvement section"""
        points = []
        
        # Add missed points
        if analysis['key_points_missed']:
            points.append(f"Missed {len(analysis['key_points_missed'])} key points from the suggested approach.")
        
        # Add compliance issues
        compliance_issues = []
        for issue, is_violated in analysis['compliance_analysis'].items():
            if is_violated:
                compliance_issues.append(issue.replace('_', ' ').title())
        
        if compliance_issues:
            points.append(f"Areas for improvement in: {', '.join(compliance_issues)}.")
        
        # Add RAG-enhanced points
        if rag_enhanced['areas_for_improvement']:
            points.extend(rag_enhanced['areas_for_improvement'])
        
        return " ".join(points) if points else "No specific areas for improvement identified."
    
    def _generate_specific_recommendations(self, analysis: Dict[str, Any], rag_enhanced: Dict[str, Any]) -> str:
        """Generate specific recommendations section"""
        recommendations = []
        
        # Add recommendations based on missed points
        for missed_point in analysis['key_points_missed'][:3]:  # Limit to top 3
            recommendations.append(f"Consider addressing: {missed_point}")
        
        # Add RAG-enhanced recommendations
        if rag_enhanced['specific_recommendations']:
            recommendations.extend(rag_enhanced['specific_recommendations'])
        
        return " ".join(recommendations) if recommendations else "No specific recommendations at this time."
