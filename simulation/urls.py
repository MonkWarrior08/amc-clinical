from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.auth_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('session-history/', views.session_history, name='session_history'),
    path('categories/', views.categories, name='categories'),
    path('cases/<str:category>/', views.case_list, name='case_list'),
    path('case/<int:case_id>/', views.case_detail, name='case_detail'),
    path('simulation/<int:case_id>/', views.case_simulation, name='case_simulation'),
    path('feedback/<int:case_id>/', views.session_feedback, name='session_feedback'),
]