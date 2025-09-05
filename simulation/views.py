from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
import json


# Create your views here.
def home(request):
    """Welcome page - redirects to auth if not logged in, dashboard if logged in"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'simulation/welcome.html')


def auth_view(request):
    """Authentication page with login and registration forms"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Handle both login and registration from the same form
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        if 'login-email' in data or 'email' in data:
            # Handle login
            email = data.get('login-email') or data.get('email')
            password = data.get('login-password') or data.get('password')
            
            # For now, use email as username (you might want to create a custom user model later)
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True, 'redirect': reverse('dashboard')})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'})
        
        elif 'register-email' in data:
            # Handle registration
            form = UserCreationForm({
                'username': data.get('register-email'),
                'password1': data.get('register-password'),
                'password2': data.get('register-password-confirm')
            })
            
            if form.is_valid():
                user = form.save()
                login(request, user)
                return JsonResponse({'success': True, 'redirect': reverse('dashboard')})
            else:
                errors = dict(form.errors)
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
    return render(request, 'simulation/cases/case_list.html', {'category': category})


@login_required
def case_detail(request, case_id):
    return render(request, 'simulation/cases/case_briefing.html', {'case_id': case_id})


@login_required
def case_simulation(request, case_id):
    return render(request, 'simulation/cases/simulation.html', {'case_id': case_id})


@login_required
def session_feedback(request, case_id):
    return render(request, 'simulation/feedback/feedback_report.html', {'case_id': case_id})