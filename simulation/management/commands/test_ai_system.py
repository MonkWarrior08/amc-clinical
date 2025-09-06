"""
Management command to test the AI system

Usage: python manage.py test_ai_system
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from simulation.models import Case
from simulation.ai_core.ai_service import ai_service
from simulation.db_utils import MedicalCasesQuery
import json

class Command(BaseCommand):
    help = 'Test the AI system with a sample case'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--case-id',
            type=str,
            help='Case ID to test with (optional)',
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Run in interactive mode',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting AI system test...'))
        
        # Get a test case
        case_id = options.get('case_id')
        if not case_id:
            # Get the first available case
            cases = Case.objects.all()[:1]
            if not cases:
                self.stdout.write(self.style.ERROR('No cases found in database'))
                return
            case_id = cases[0].case_id
        
        self.stdout.write(f'Testing with case: {case_id}')
        
        # Get case data
        try:
            case_obj = Case.objects.get(case_id=case_id)
            case_data = case_obj  # Pass the model instance directly
        except Case.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Case {case_id} not found'))
            return
        
        # Create a test user
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com'}
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write('Created test user')
        
        # Start a session
        try:
            session_id = ai_service.start_session(user, case_data)
            self.stdout.write(self.style.SUCCESS(f'Session started: {session_id}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to start session: {e}'))
            return
        
        if options.get('interactive'):
            self._run_interactive_test(session_id)
        else:
            self._run_automated_test(session_id)
    
    def _run_interactive_test(self, session_id):
        """Run interactive test"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('INTERACTIVE MODE')
        self.stdout.write('Type "quit" to exit, "examiner" to test examiner workflow')
        self.stdout.write('='*50 + '\n')
        
        while True:
            user_input = input('\nDoctor: ')
            
            if user_input.lower() == 'quit':
                break
            
            try:
                response = ai_service.process_user_input(session_id, user_input)
                
                if 'error' in response:
                    self.stdout.write(self.style.ERROR(f'Error: {response["error"]}'))
                    continue
                
                if response['type'] == 'patient_response':
                    self.stdout.write(f'Patient: {response["response"]}')
                elif response['type'] == 'examiner_response':
                    self.stdout.write(f'Examiner: {response["response"]}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing input: {e}'))
        
        # End session and generate feedback
        self.stdout.write('\nEnding session and generating feedback...')
        try:
            result = ai_service.end_session(session_id)
            self._display_feedback(result['feedback'])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating feedback: {e}'))
    
    def _run_automated_test(self, session_id):
        """Run automated test with sample interactions"""
        self.stdout.write('\nRunning automated test...')
        
        # Sample interactions
        test_inputs = [
            "Hello, I'm Dr. Smith. How are you feeling today?",
            "Can you tell me what brought you in today?",
            "How long have you been experiencing these symptoms?",
            "Examiner: I would like to examine the patient's vital signs",
            "Are you taking any medications?",
            "Do you have any allergies?",
            "Thank you for coming in today. We'll get you feeling better soon."
        ]
        
        for i, user_input in enumerate(test_inputs, 1):
            self.stdout.write(f'\n--- Interaction {i} ---')
            self.stdout.write(f'Doctor: {user_input}')
            
            try:
                response = ai_service.process_user_input(session_id, user_input)
                
                if 'error' in response:
                    self.stdout.write(self.style.ERROR(f'Error: {response["error"]}'))
                    continue
                
                if response['type'] == 'patient_response':
                    self.stdout.write(f'Patient: {response["response"]}')
                elif response['type'] == 'examiner_response':
                    self.stdout.write(f'Examiner: {response["response"]}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing input: {e}'))
        
        # End session and generate feedback
        self.stdout.write('\n--- Ending Session ---')
        try:
            result = ai_service.end_session(session_id)
            self._display_feedback(result['feedback'])
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error generating feedback: {e}'))
    
    def _display_feedback(self, feedback):
        """Display feedback in a formatted way"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('FEEDBACK REPORT')
        self.stdout.write('='*60)
        
        # Overall score
        status = "PASS" if feedback['pass_fail'] else "FAIL"
        self.stdout.write(f'Overall Score: {feedback["overall_score"]}/100 ({status})')
        
        # What went well
        self.stdout.write(f'\nWhat Went Well:')
        self.stdout.write(f'{feedback["what_went_well"]}')
        
        # Areas for improvement
        self.stdout.write(f'\nAreas for Improvement:')
        self.stdout.write(f'{feedback["areas_for_improvement"]}')
        
        # Specific recommendations
        self.stdout.write(f'\nSpecific Recommendations:')
        self.stdout.write(f'{feedback["specific_recommendations"]}')
        
        # Key points covered
        if feedback['key_points_covered']:
            self.stdout.write(f'\nKey Points Covered ({len(feedback["key_points_covered"])}):')
            for point in feedback['key_points_covered'][:5]:  # Show first 5
                self.stdout.write(f'  - {point}')
        
        # Key points missed
        if feedback['key_points_missed']:
            self.stdout.write(f'\nKey Points Missed ({len(feedback["key_points_missed"])}):')
            for point in feedback['key_points_missed'][:5]:  # Show first 5
                self.stdout.write(f'  - {point}')
        
        # RAG sources
        if feedback['rag_sources']:
            self.stdout.write(f'\nRAG Sources Used: {len(feedback["rag_sources"])}')
        
        self.stdout.write('='*60)
