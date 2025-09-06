from django.urls import path
from . import views
from .api_views import (
    StartSessionView, InteractView, EndSessionView, 
    SessionStateView, ResumePatientView, GetFeedbackView, SessionHistoryView
)

urlpatterns = [
    path('', views.home, name='home'),
    path('pricing/', views.pricing, name='pricing'),
    path('auth/', views.auth_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('session-history/', views.session_history, name='session_history'),
    path('categories/', views.categories, name='categories'),
    path('cases/<str:category>/', views.case_list, name='case_list'),
    path('case/<str:case_id>/', views.case_detail, name='case_detail'),
    path('simulation/<str:case_id>/', views.case_simulation, name='case_simulation'),
    path('feedback/<str:case_id>/', views.session_feedback, name='session_feedback'),
    
    # API endpoints for AI interactions
    path('api/start-session/', StartSessionView.as_view(), name='api_start_session'),
    path('api/interact/', InteractView.as_view(), name='api_interact'),
    path('api/end-session/', EndSessionView.as_view(), name='api_end_session'),
    path('api/session-state/<str:session_id>/', SessionStateView.as_view(), name='api_session_state'),
    path('api/resume-patient/', ResumePatientView.as_view(), name='api_resume_patient'),
    path('api/feedback/<str:session_id>/', GetFeedbackView.as_view(), name='api_get_feedback'),
    path('api/session-history/', SessionHistoryView.as_view(), name='api_session_history'),
]