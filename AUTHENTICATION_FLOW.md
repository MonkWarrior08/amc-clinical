r# Authentication Flow Documentation

## Overview
This document describes the authentication flow implemented in the AMC Clinical Exam Simulator application.

## Flow Description

### 1. Welcome Page (`/`)
- **File**: `simulation/templates/simulation/welcome.html`
- **View**: `home()` in `simulation/views.py`
- **Behavior**:
  - If user is **not authenticated**: Shows welcome page with login/register buttons
  - If user is **authenticated**: Redirects to dashboard (`/dashboard/`)

### 2. Authentication Page (`/auth/`)
- **File**: `simulation/templates/registration/auth.html`
- **View**: `auth_view()` in `simulation/views.py`
- **Behavior**:
  - If user is **not authenticated**: Shows login and registration forms
  - If user is **authenticated**: Redirects to dashboard (`/dashboard/`)
  - Handles both login and registration via AJAX POST requests
  - Returns JSON responses for success/error states

### 3. Dashboard Page (`/dashboard/`)
- **File**: `simulation/templates/simulation/dashboard.html`
- **View**: `dashboard()` in `simulation/views.py`
- **Behavior**:
  - If user is **not authenticated**: Redirects to auth page (`/auth/`)
  - If user is **authenticated**: Shows dashboard with user stats and navigation

### 4. Logout (`/logout/`)
- **View**: `logout_view()` in `simulation/views.py`
- **Behavior**: Logs out user and redirects to welcome page (`/`)

## URL Configuration

```python
urlpatterns = [
    path('', views.home, name='home'),                    # Welcome page
    path('auth/', views.auth_view, name='auth'),          # Authentication
    path('logout/', views.logout_view, name='logout'),    # Logout
    path('dashboard/', views.dashboard, name='dashboard'), # Dashboard
    # ... other URLs
]
```

## Django Settings

```python
# Authentication redirects
LOGIN_REDIRECT_URL = '/dashboard/'  # After successful login
LOGOUT_REDIRECT_URL = '/'           # After logout
LOGIN_URL = '/auth/'                # Where to redirect for login
```

## User Flow Examples

### New User Registration
1. User visits `/` → Sees welcome page
2. User clicks "Start Your Journey" → Goes to `/auth/`
3. User fills registration form → Submits via AJAX
4. On success → Redirected to `/dashboard/`

### Existing User Login
1. User visits `/` → Sees welcome page
2. User clicks "Access Your Account" → Goes to `/auth/`
3. User fills login form → Submits via AJAX
4. On success → Redirected to `/dashboard/`

### Authenticated User
1. User visits `/` → Automatically redirected to `/dashboard/`
2. User can access all protected pages
3. User clicks logout → Redirected to `/`

## Template Structure

```
simulation/templates/
├── registration/
│   └── auth.html              # Login/Register forms
└── simulation/
    ├── welcome.html           # Landing page
    ├── dashboard.html         # Main dashboard
    ├── category_select.html   # Category selection
    ├── cases/
    │   ├── case_list.html
    │   ├── case_briefing.html
    │   └── simulation.html
    ├── feedback/
    │   └── feedback_report.html
    └── sessions/
        └── session_history.html
```

## Security Features

- CSRF protection on all forms
- Login required decorator on protected views
- Automatic redirects for unauthenticated users
- Secure password validation using Django's built-in validators

## Testing

The authentication flow has been tested and verified to work correctly:
- Welcome page shows for unauthenticated users
- Auth page shows login/register forms
- Dashboard redirects unauthenticated users to auth
- Login/logout functionality works properly
- Authenticated users are redirected from welcome to dashboard
