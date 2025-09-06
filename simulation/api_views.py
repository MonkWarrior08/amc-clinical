"""
API views for AI interactions in Clinical AI ExamPro

This module provides REST API endpoints for the AI system,
including session management and real-time interactions.
"""

import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404

from .models import Case, Session, Feedback, AIAgentState
from .ai_core.ai_service import ai_service
from .db_utils import MedicalCasesQuery
from django.views.decorators.http import require_POST
from django.conf import settings
from openai import OpenAI
import base64

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class StartSessionView(View):
    """API endpoint to start a new AI session"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            case_id = data.get('case_id')
            
            if not case_id:
                return JsonResponse({'error': 'case_id is required'}, status=400)
            
            # Get case data from database
            db_query = MedicalCasesQuery()
            case_data = db_query.get_case_with_content(case_id)
            db_query.close()
            
            if not case_data:
                return JsonResponse({'error': 'Case not found'}, status=404)
            
            # Start AI session
            session_id = ai_service.start_session(request.user, case_data)
            
            # Create Django session record
            case_obj = get_object_or_404(Case, case_id=case_id)
            session_obj = Session.objects.create(
                user=request.user,
                case=case_obj,
                session_id=session_id
            )
            
            # Create AI agent state
            AIAgentState.objects.create(
                session=session_obj,
                patient_persona=case_data.get('instructions_for_patient', '')
            )
            
            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'case_id': case_id,
                'message': 'Session started successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class InteractView(View):
    """API endpoint for user interactions during a session"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            user_input = data.get('user_input')
            
            if not session_id or not user_input:
                return JsonResponse({'error': 'session_id and user_input are required'}, status=400)
            
            # Process input through AI service
            response = ai_service.process_user_input(session_id, user_input)
            
            if 'error' in response:
                return JsonResponse(response, status=404)
            
            # Update session transcript
            try:
                session_obj = Session.objects.get(session_id=session_id)
                session_obj.add_to_transcript('Doctor', user_input)
                
                if response['type'] == 'patient_response':
                    session_obj.add_to_transcript('Patient', response['response'])
                elif response['type'] == 'examiner_response':
                    session_obj.add_to_transcript('Examiner', response['response'])
                
                # Update AI agent state
                ai_state = AIAgentState.objects.get(session=session_obj)
                ai_state.patient_paused = response.get('patient_paused', False)
                ai_state.save()
                
            except Session.DoesNotExist:
                pass  # Continue even if session record not found
            
            return JsonResponse({
                'success': True,
                'response': response['response'],
                'type': response['type'],
                'patient_paused': response.get('patient_paused', False)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class EndSessionView(View):
    """API endpoint to end a session and generate feedback"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            
            if not session_id:
                return JsonResponse({'error': 'session_id is required'}, status=400)
            
            # End session and generate feedback
            result = ai_service.end_session(session_id)
            
            if 'error' in result:
                return JsonResponse(result, status=404)
            
            # Save feedback to database
            try:
                session_obj = Session.objects.get(session_id=session_id)
                session_obj.is_active = False
                session_obj.save()
                
                # Create feedback record
                feedback_obj = Feedback.objects.create(
                    session=session_obj,
                    overall_score=result['feedback']['overall_score'],
                    pass_fail=result['feedback']['pass_fail'],
                    what_went_well=result['feedback']['what_went_well'],
                    areas_for_improvement=result['feedback']['areas_for_improvement'],
                    specific_recommendations=result['feedback']['specific_recommendations'],
                    key_points_covered=result['feedback']['key_points_covered'],
                    key_points_missed=result['feedback']['key_points_missed'],
                    compliance_analysis=result['feedback']['compliance_analysis'],
                    rag_sources=result['feedback']['rag_sources'],
                    generation_time_seconds=result['feedback']['generation_time_seconds']
                )
                
                # Update AI agent state
                ai_state = AIAgentState.objects.get(session=session_obj)
                ai_state.feedback_generated = True
                ai_state.rag_queries_used = result['feedback']['rag_sources']
                ai_state.save()
                
            except Session.DoesNotExist:
                pass  # Continue even if session record not found
            
            return JsonResponse({
                'success': True,
                'session_id': session_id,
                'feedback': result['feedback'],
                'transcript': result['transcript']
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(login_required, name='dispatch')
class SessionStateView(View):
    """API endpoint to get current session state"""
    
    def get(self, request, session_id):
        try:
            state = ai_service.get_session_state(session_id)
            
            if 'error' in state:
                return JsonResponse(state, status=404)
            
            return JsonResponse({
                'success': True,
                'state': state
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ResumePatientView(View):
    """API endpoint to resume patient agent after examiner interaction"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            
            if not session_id:
                return JsonResponse({'error': 'session_id is required'}, status=400)
            
            success = ai_service.resume_patient(session_id)
            
            if not success:
                return JsonResponse({'error': 'Session not found'}, status=404)
            
            return JsonResponse({
                'success': True,
                'message': 'Patient agent resumed'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(login_required, name='dispatch')
class GetFeedbackView(View):
    """API endpoint to get feedback for a completed session"""
    
    def get(self, request, session_id):
        try:
            session_obj = get_object_or_404(Session, session_id=session_id)
            
            try:
                feedback_obj = Feedback.objects.get(session=session_obj)
                
                return JsonResponse({
                    'success': True,
                    'feedback': {
                        'overall_score': feedback_obj.overall_score,
                        'pass_fail': feedback_obj.pass_fail,
                        'what_went_well': feedback_obj.what_went_well,
                        'areas_for_improvement': feedback_obj.areas_for_improvement,
                        'specific_recommendations': feedback_obj.specific_recommendations,
                        'key_points_covered': feedback_obj.key_points_covered,
                        'key_points_missed': feedback_obj.key_points_missed,
                        'compliance_analysis': feedback_obj.compliance_analysis,
                        'rag_sources': feedback_obj.rag_sources,
                        'generated_at': feedback_obj.generated_at.isoformat()
                    }
                })
                
            except Feedback.DoesNotExist:
                return JsonResponse({'error': 'Feedback not found for this session'}, status=404)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(login_required, name='dispatch')
class SessionHistoryView(View):
    """API endpoint to get user's session history"""
    
    def get(self, request):
        try:
            sessions = Session.objects.filter(user=request.user).order_by('-started_at')
            
            session_list = []
            for session in sessions:
                session_data = {
                    'session_id': session.session_id,
                    'case_id': session.case.case_id,
                    'case_category': session.case.category,
                    'started_at': session.started_at.isoformat(),
                    'ended_at': session.ended_at.isoformat() if session.ended_at else None,
                    'is_active': session.is_active,
                    'duration_minutes': session.duration_minutes
                }
                
                # Add feedback if available
                try:
                    feedback = Feedback.objects.get(session=session)
                    session_data['feedback'] = {
                        'overall_score': feedback.overall_score,
                        'pass_fail': feedback.pass_fail,
                        'generated_at': feedback.generated_at.isoformat()
                    }
                except Feedback.DoesNotExist:
                    session_data['feedback'] = None
                
                session_list.append(session_data)
            
            return JsonResponse({
                'success': True,
                'sessions': session_list
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class TextToSpeechView(View):
    """Generate TTS audio from text using OpenAI and return as base64 MP3"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            text = data.get('text', '').strip()
            voice = data.get('voice', 'alloy')
            model = data.get('model', 'gpt-4o-mini-tts')
            if not text:
                return JsonResponse({'error': 'text is required'}, status=400)

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            result = client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                format='mp3'
            )
            # openai>=1.0 returns bytes in result.content or result.read()
            audio_bytes = result.read() if hasattr(result, 'read') else result.content
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

            return JsonResponse({'success': True, 'audio_base64': audio_b64, 'mime': 'audio/mpeg'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
