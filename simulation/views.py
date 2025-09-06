from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from .forms import CustomUserCreationForm
from .db_utils import MedicalCasesQuery
import json


# Create your views here.
def home(request):
    """Welcome page - redirects to auth if not logged in, dashboard if logged in"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'simulation/welcome.html')


def pricing(request):
    """Pricing page"""
    return render(request, 'simulation/pricing.html')


def auth_view(request):
    """Authentication page with login and registration forms"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Handle both login and registration from the same form
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        if 'email' in data and 'first_name' not in data:
            # Handle login - only if it's not a registration form
            email = data.get('email')
            password = data.get('password')
            
            # For now, use email as username (you might want to create a custom user model later)
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'redirect': reverse('dashboard')})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'})
        
        elif 'email' in data and 'first_name' in data:
            # Handle registration - check for both email and first_name to distinguish from login
            form = CustomUserCreationForm({
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'email': data.get('email'),
                'password1': data.get('password1'),
                'password2': data.get('password2'),
                'terms_agreement': data.get('terms_agreement') == 'on',
                'marketing_emails': data.get('marketing_emails') == 'on'
            })
            
            if form.is_valid():
                try:
                    user = form.save()
                    login(request, user)
                    return JsonResponse({'success': True, 'redirect': reverse('dashboard')})
                except Exception as e:
                    return JsonResponse({'success': False, 'error': f'Registration failed: {str(e)}'})
            else:
                errors = dict(form.errors)
                print(f"Form validation errors: {errors}")  # Debug logging
                return JsonResponse({'success': False, 'errors': errors})
    
    return render(request, 'registration/auth.html')


def logout_view(request):
    """Logout user and redirect to welcome page"""
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    return render(request, 'simulation/dashboard.html')


@login_required
def session_history(request):
    return render(request, 'simulation/sessions/session_history.html')


@login_required
def categories(request):
    return render(request, 'simulation/category_select.html')


@login_required
def case_list(request, category):
    """Display cases for a specific category with database content"""
    try:
        db_query = MedicalCasesQuery()
        cases = db_query.get_cases_with_content_by_category(category)
        db_query.close()
        
        # Convert category name to display format
        category_display = category.replace('_', ' ').title()
        
        # Get category icon mapping
        category_icons = {
            'cardiovascular_system': 'heart',
            'dermatology': 'skin',
            'mental_health': 'brain',
            'emergency_medicine': 'alert-triangle',
            'child_health': 'baby',
            'aged_care': 'user-check',
            'adolescent_health': 'users',
            'challenging_consultation': 'message-circle',
            'ear_nose_and_throat': 'ear',
            'endocrinology': 'activity',
            'eyes': 'eye',
            'gastroenterology': 'stomach',
            'infectious_disease': 'shield',
            'mens_health': 'user',
            'musculoskeletal_medicine': 'bone'
        }
        
        category_icon = category_icons.get(category.lower(), 'file-text')
        
        context = {
            'category': category,
            'category_name': category_display,
            'category_icon': category_icon,
            'cases': cases,
            'cases_count': len(cases),
            'completion_rate': 0  # TODO: Calculate from user progress
        }
        
        return render(request, 'simulation/cases/case_list.html', context)
        
    except Exception as e:
        # Fallback to static data if database fails
        messages.error(request, f"Error loading cases: {str(e)}")
        return render(request, 'simulation/cases/case_list.html', {
            'category': category,
            'category_name': category.replace('_', ' ').title(),
            'category_icon': 'file-text',
            'cases': [],
            'cases_count': 0,
            'completion_rate': 0
        })


@login_required
def case_detail(request, case_id):
    """Display case briefing with database content"""
    try:
        db_query = MedicalCasesQuery()
        case_data = db_query.get_case_with_content(case_id)
        db_query.close()
        
        if not case_data:
            messages.error(request, f"Case '{case_id}' not found")
            return redirect('categories')
        
        # Create a mock case object for template compatibility
        class MockCase:
            def __init__(self, data):
                self.case_id = data.get('case_id', case_id)
                self.patient_name = data.get('patient_name', 'Patient')
                self.difficulty = data.get('difficulty', 'Beginner')
                self.duration = data.get('duration', 20)
                self.category_name = data.get('category', 'General')
                self.scenario = data.get('scenario', '')
                self.instruction = data.get('instruction', '')
        
        case = MockCase(case_data)
        
        context = {
            'case_id': case_id,
            'case': case,
            'category': case_data.get('category_name', 'Unknown'),
            'category_name': case_data.get('category_name', 'Unknown')
        }
        
        return render(request, 'simulation/cases/case_briefing.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading case: {str(e)}")
        return redirect('categories')


@login_required
def case_simulation(request, case_id):
    try:
        # Get case data from database
        db_query = MedicalCasesQuery()
        case_data = db_query.get_case_with_content(case_id)
        db_query.close()
        
        if not case_data:
            messages.error(request, 'Case not found')
            return redirect('categories')
        
        # Create a mock case object for template compatibility
        class MockCase:
            def __init__(self, data):
                self.case_id = data.get('case_id', case_id)
                self.patient_name = data.get('patient_name', 'Patient')
                self.difficulty = data.get('difficulty', 'Beginner')
                self.duration = data.get('duration', 20)
                self.category_name = data.get('category', 'General')
        
        case = MockCase(case_data)
        
        context = {
            'case': case,
            'case_id': case_id,
            'category_icon': 'heart'  # Default icon
        }
        
        return render(request, 'simulation/cases/simulation.html', context)
        
    except Exception as e:
        messages.error(request, f"Error loading case: {str(e)}")
        return redirect('categories')


@login_required
def session_feedback(request, case_id):
    """Render personalized AI feedback for the user's latest session of this case"""
    from .models import Session, Feedback, Case

    # Find the case
    try:
        case = Case.objects.get(case_id=case_id)
    except Case.DoesNotExist:
        messages.error(request, 'Case not found')
        return redirect('categories')

    # Allow explicit session selection via query param
    selected_session_id = request.GET.get('session_id')
    if selected_session_id:
        session_obj = Session.objects.filter(user=request.user, case=case, session_id=selected_session_id).first()
    else:
        # Get the most recent session for this user and case
        session_obj = (
            Session.objects.filter(user=request.user, case=case)
            .order_by('-ended_at', '-started_at')
            .first()
        )

    feedback_data = None
    # Compute time used and expose an 8-minute time limit for the OSCE station
    duration_used = None
    if session_obj and getattr(session_obj, 'started_at', None) and getattr(session_obj, 'ended_at', None):
        try:
            delta_seconds = (session_obj.ended_at - session_obj.started_at).total_seconds()
            duration_used = int(round(delta_seconds / 60.0))
        except Exception:
            duration_used = None
    # Fallback to stored minutes if available
    if duration_used is None:
        duration_used = getattr(session_obj, 'duration_minutes', None)

    session_ctx = {
        'patient_name': getattr(case, 'case_id', 'Patient'),
        'completed_date': getattr(session_obj, 'ended_at', None) or getattr(session_obj, 'started_at', None),
        'duration': getattr(session_obj, 'duration_minutes', None) or '',
        'duration_used': duration_used,
        'time_limit': 8,
    }
    transcript_text = ''

    if session_obj:
        try:
            feedback = Feedback.objects.get(session=session_obj)
            # Map model fields to template-friendly structure
            # Ensure textual fields are normalized to lists for template iteration
            def to_list(value):
                if value is None:
                    return []
                if isinstance(value, list):
                    return value
                if isinstance(value, str):
                    # Split on newlines or bullet separators; trim empties
                    parts = [p.strip('-• \t').strip() for p in value.split('\n')]
                    parts = [p for p in parts if p]
                    if len(parts) > 1:
                        return parts
                    # Fallback: try semicolons
                    parts = [p.strip() for p in value.split(';') if p.strip()]
                    return parts if parts else ([value] if value.strip() else [])
                return [str(value)]

            feedback_data = {
                'overall_score': feedback.overall_score,
                'outcome': 'pass' if feedback.pass_fail else 'fail',
                'what_went_well': to_list(getattr(feedback, 'what_went_well', None)),
                'areas_for_improvement': to_list(getattr(feedback, 'areas_for_improvement', None)),
                'specific_recommendations': to_list(getattr(feedback, 'specific_recommendations', None)),
                'key_points_covered': to_list(getattr(feedback, 'key_points_covered', None)),
                'key_points_missed': to_list(getattr(feedback, 'key_points_missed', None)),
                'compliance_analysis': getattr(feedback, 'compliance_analysis', {}) or {},
                'rag_sources': getattr(feedback, 'rag_sources', []) or [],
            }
        except Feedback.DoesNotExist:
            pass
        # Pull transcript from the session record
        transcript_text = session_obj.transcript or ''

    # Build marksheet data
    key_steps = []
    covered = (feedback_data or {}).get('key_points_covered') or []
    missed = (feedback_data or {}).get('key_points_missed') or []
    # take up to 3 from covered then missed
    for txt in covered[:3]:
        key_steps.append({'text': txt, 'yes': True})
    if len(key_steps) < 3:
        for txt in missed:
            key_steps.append({'text': txt, 'yes': False})
            if len(key_steps) >= 3:
                break

    comp = (feedback_data or {}).get('compliance_analysis') or {}
    overall = (feedback_data or {}).get('overall_score') or 0
    # Simple heuristics for 1-7 ratings
    def map_score(x):
        try:
            return max(1, min(7, int(round((x/100.0)*7))))
        except Exception:
            return 4
    # (ratings will be computed after deriving domain percentages below)

    # Derive domain scores (history, examination, communication, reasoning) from AI feedback
    def classify_category(text: str) -> str | None:
        t = (text or '').lower()
        if any(k in t for k in ['examin', 'palpat', 'auscultat', 'inspect', 'percuss', 'vital', 'bp', 'blood pressure']):
            return 'examination'
        if any(k in t for k in ['history', 'hx', 'symptom', 'onset', 'duration', 'medication', 'allerg', 'family', 'social', 'socrates']):
            return 'history'
        if any(k in t for k in ['explain', 'consent', 'rapport', 'empathy', 'reassur', 'open-ended', 'summar', 'communicat', 'ask if', 'any questions']):
            return 'communication'
        if any(k in t for k in ['diagnos', 'differential', 'investig', 'reason', 'management', 'plan', 'interpret']):
            return 'reasoning'
        return None

    covered_points = (feedback_data or {}).get('key_points_covered') or []
    missed_points = (feedback_data or {}).get('key_points_missed') or []
    compliance = (feedback_data or {}).get('compliance_analysis') or {}

    # Tally points by category
    tallies = {'history': {'covered': 0, 'total': 0},
               'examination': {'covered': 0, 'total': 0},
               'communication': {'covered': 0, 'total': 0},
               'reasoning': {'covered': 0, 'total': 0}}

    for p in covered_points:
        cat = classify_category(p)
        if cat:
            tallies[cat]['covered'] += 1
            tallies[cat]['total'] += 1
    for p in missed_points:
        cat = classify_category(p)
        if cat:
            tallies[cat]['total'] += 1

    def pct(covered: int, total: int, fallback: float) -> int:
        if total > 0:
            return max(0, min(100, int(round((covered / float(total)) * 100))))
        # Fallback to overall if we cannot classify items
        return int(round(fallback))

    # Start from overall as fallback baseline
    baseline = float(overall or 0)
    history_pct = pct(tallies['history']['covered'], tallies['history']['total'], baseline)
    exam_pct = pct(tallies['examination']['covered'], tallies['examination']['total'], baseline)
    comm_pct = pct(tallies['communication']['covered'], tallies['communication']['total'], baseline)
    reason_pct = pct(tallies['reasoning']['covered'], tallies['reasoning']['total'], baseline)

    # Adjust communication with compliance signals
    if compliance.get('used_jargon'):
        comm_pct = max(0, comm_pct - 8)
    if not compliance.get('maintained_rapport', True):
        comm_pct = max(0, comm_pct - 8)

    def label_for(score: int) -> str:
        if score >= 85:
            return 'Excellent'
        if score >= 75:
            return 'Very Good'
        if score >= 65:
            return 'Good'
        if score >= 50:
            return 'Satisfactory'
        return 'Needs Improvement'

    # Enrich feedback dict for template consumption
    if feedback_data is None:
        feedback_data = {}
    feedback_data.update({
        'history_score': history_pct,
        'examination_score': exam_pct,
        'communication_score': comm_pct,
        'reasoning_score': reason_pct,
        'history_label': label_for(history_pct),
        'examination_label': label_for(exam_pct),
        'communication_label': label_for(comm_pct),
        'reasoning_label': label_for(reason_pct),
    })

    # Compute marksheet ratings now that domain percentages are available
    approach_score = 6 if (compliance.get('maintained_rapport') and not compliance.get('used_jargon')) else 4
    history_score = map_score(history_pct)
    examination_score = map_score(exam_pct)
    diagnosis_score = map_score(reason_pct)
    global_rating = map_score(overall)

    marksheet = {
        'topic': case_id.replace('_', ' ').title(),
        'candidate_name': request.user.get_full_name() or request.user.username,
        'key_steps': key_steps,
        'ratings': {
            'approach': approach_score,
            'history': history_score,
            'examination': examination_score,
            'diagnosis': diagnosis_score,
            'global_rating': global_rating,
            'pass_fail': (feedback_data or {}).get('outcome') == 'pass'
        }
    }

    context = {
        'case_id': case_id,
        'session': session_ctx,
        'feedback': feedback_data or {},
        'transcript': transcript_text,
        'marksheet': marksheet,
        'category_slug': getattr(case, 'category', ''),
    }

    return render(request, 'simulation/feedback/feedback_report.html', context)