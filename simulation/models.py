from django.db import models
from django.contrib.auth.models import User
import json

class Case(models.Model):
    """Medical case model with all necessary fields for AI workflows"""
    case_id = models.CharField(max_length=100, unique=True, primary_key=True)
    category = models.CharField(max_length=100)
    
    # Patient information
    scenario = models.TextField(blank=True)
    instructions_for_patient = models.TextField(blank=True)
    gender = models.CharField(max_length=10, blank=True)
    age = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    
    # Doctor instructions
    instruction_for_doc = models.TextField(blank=True)
    case_type = models.CharField(max_length=100, blank=True)
    
    # Examination details
    examination_details = models.TextField(blank=True)
    info_for_facilitator_exam_findings = models.TextField(blank=True)
    
    # Suggested approach for evaluation
    specific_questions = models.TextField(blank=True)
    management_plan = models.TextField(blank=True)
    case_commentary = models.TextField(blank=True)
    pitfalls = models.TextField(blank=True)
    
    # Additional fields
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.case_id} - {self.category}"
    
    def get_suggested_approach(self):
        """Get the complete suggested approach as a dictionary"""
        return {
            'specific_questions': self.specific_questions,
            'examination_details': self.examination_details,
            'management_plan': self.management_plan,
            'case_commentary': self.case_commentary,
            'pitfalls': self.pitfalls
        }

class Session(models.Model):
    """User session for a specific case"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    
    # Session state
    is_active = models.BooleanField(default=True)
    current_turn = models.IntegerField(default=0)
    patient_paused = models.BooleanField(default=False)
    
    # Conversation data
    transcript = models.TextField(blank=True)
    conversation_history = models.JSONField(default=list)
    
    # Session metadata
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"Session {self.session_id} - {self.user.username} - {self.case.case_id}"
    
    def add_to_transcript(self, speaker, message):
        """Add a message to the transcript"""
        if not self.transcript:
            self.transcript = ""
        
        self.transcript += f"{speaker}: {message}\n"
        self.save()
    
    def add_to_conversation_history(self, speaker, message, metadata=None):
        """Add a message to the conversation history with metadata"""
        if not self.conversation_history:
            self.conversation_history = []
        
        entry = {
            'turn': self.current_turn,
            'speaker': speaker,
            'message': message,
            'timestamp': models.DateTimeField(auto_now_add=True).value_from_object(self),
            'metadata': metadata or {}
        }
        
        self.conversation_history.append(entry)
        self.current_turn += 1
        self.save()

class Feedback(models.Model):
    """Generated feedback for a completed session"""
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    
    # Feedback scores
    overall_score = models.FloatField()
    pass_fail = models.BooleanField()
    
    # Feedback content
    what_went_well = models.TextField()
    areas_for_improvement = models.TextField()
    specific_recommendations = models.TextField()
    
    # Detailed analysis
    key_points_covered = models.JSONField(default=list)
    key_points_missed = models.JSONField(default=list)
    compliance_analysis = models.JSONField(default=dict)
    
    # RAG sources used
    rag_sources = models.JSONField(default=list)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generation_time_seconds = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        status = "PASS" if self.pass_fail else "FAIL"
        return f"Feedback for {self.session} - {status} ({self.overall_score}/100)"

class AIAgentState(models.Model):
    """Store AI agent state for sessions"""
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    
    # Patient agent state
    patient_persona = models.TextField(blank=True)
    patient_memory = models.JSONField(default=list)
    patient_context = models.JSONField(default=dict)
    
    # Examiner state
    last_examiner_request = models.TextField(blank=True)
    examiner_findings_retrieved = models.BooleanField(default=False)
    
    # Feedback agent state
    feedback_generated = models.BooleanField(default=False)
    rag_queries_used = models.JSONField(default=list)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"AI State for {self.session}"
