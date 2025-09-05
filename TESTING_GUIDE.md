# AMC Clinical Exam Simulator - Testing Guide

## 🚀 Webapp is Running!

**URL:** http://localhost:8001/

## 📋 Testing Checklist

### 1. Welcome Page Testing
**URL:** http://localhost:8001/

**What to test:**
- [ ] Page loads correctly with medical theme
- [ ] "Access Your Account" button works (redirects to auth page)
- [ ] "Start Your Journey" button works (redirects to auth page)
- [ ] Page shows for unauthenticated users
- [ ] If you're logged in, it should redirect to dashboard

### 2. Authentication Page Testing
**URL:** http://localhost:8001/auth/

#### Login Tab Testing:
- [ ] Login form displays correctly
- [ ] Email field accepts input
- [ ] Password field accepts input
- [ ] "Remember me" checkbox works
- [ ] Password visibility toggle works (eye icon)
- [ ] "Sign In to Your Account" button is clickable

#### Registration Tab Testing:
- [ ] Click "Register" tab to switch forms
- [ ] First Name field accepts input
- [ ] Last Name field accepts input
- [ ] Email field accepts input
- [ ] Password field accepts input
- [ ] Confirm Password field accepts input
- [ ] Password visibility toggles work for both password fields
- [ ] Terms of Service checkbox is required
- [ ] Marketing emails checkbox is optional
- [ ] "Create Your Account" button is clickable

### 3. Registration Testing
**Test with valid data:**
- [ ] Fill in all required fields:
  - First Name: `John`
  - Last Name: `Doe`
  - Email: `john.doe@example.com`
  - Password: `testpass123`
  - Confirm Password: `testpass123`
  - Check Terms of Service
- [ ] Click "Create Your Account"
- [ ] Should redirect to dashboard
- [ ] Dashboard should show "Welcome, John!"

**Test with invalid data:**
- [ ] Try with mismatched passwords
- [ ] Try with existing email
- [ ] Try without checking Terms of Service
- [ ] Should show appropriate error messages

### 4. Login Testing
**Test with existing user:**
- [ ] Switch to Login tab
- [ ] Enter email: `john.doe@example.com`
- [ ] Enter password: `testpass123`
- [ ] Click "Sign In to Your Account"
- [ ] Should redirect to dashboard

**Test with invalid credentials:**
- [ ] Try wrong password
- [ ] Try non-existent email
- [ ] Should show error message

### 5. Dashboard Testing
**URL:** http://localhost:8001/dashboard/

**What to test:**
- [ ] Page loads with user's first name in header
- [ ] "Session History" button works
- [ ] "Logout" button works
- [ ] Stats cards display (may show 0 values initially)
- [ ] Action cards are clickable:
  - [ ] "Browse Categories" → should go to categories page
  - [ ] "Session History" → should go to session history
  - [ ] "Settings" → placeholder (not implemented yet)
  - [ ] "Help & Support" → placeholder (not implemented yet)

### 6. Navigation Testing
**Test the flow:**
- [ ] Welcome → Auth → Dashboard
- [ ] Dashboard → Logout → Welcome
- [ ] Direct access to dashboard when not logged in → should redirect to auth
- [ ] Direct access to auth when logged in → should redirect to dashboard

### 7. Categories Page Testing
**URL:** http://localhost:8001/categories/

**What to test:**
- [ ] Page loads with category selection interface
- [ ] Categories are displayed in cards
- [ ] Each category card is clickable
- [ ] Should redirect to case list for selected category

### 8. Session History Testing
**URL:** http://localhost:8001/session-history/

**What to test:**
- [ ] Page loads with session history interface
- [ ] Shows placeholder content (no actual sessions yet)

## 🐛 Common Issues to Check

### If pages don't load:
- [ ] Check if server is running: `python manage.py runserver 8001`
- [ ] Check browser console for JavaScript errors
- [ ] Check terminal for Django errors

### If forms don't submit:
- [ ] Check browser console for JavaScript errors
- [ ] Check network tab for AJAX request failures
- [ ] Verify CSRF token is present

### If redirects don't work:
- [ ] Check Django settings for LOGIN_URL, LOGIN_REDIRECT_URL
- [ ] Verify URL patterns in simulation/urls.py

## 🎯 Key Features to Verify

### ✅ Authentication Flow
- [ ] New users can register with full details
- [ ] Existing users can login
- [ ] Users are redirected appropriately based on auth status
- [ ] Logout works and redirects to welcome page

### ✅ User Experience
- [ ] Forms have real-time validation
- [ ] Error messages are clear and helpful
- [ ] Loading states work during form submission
- [ ] Responsive design works on different screen sizes

### ✅ Security
- [ ] CSRF protection is working
- [ ] Password fields are properly secured
- [ ] Email uniqueness validation works
- [ ] Protected pages redirect unauthenticated users

## 📱 Mobile Testing
- [ ] Test on mobile device or browser dev tools mobile view
- [ ] Forms should be usable on small screens
- [ ] Navigation should work on touch devices

## 🔧 Developer Tools Testing
- [ ] Open browser dev tools (F12)
- [ ] Check Console tab for any JavaScript errors
- [ ] Check Network tab for failed requests
- [ ] Check Elements tab to verify HTML structure

## 📊 Expected Results

### Successful Registration:
1. Fill form → Submit → Redirect to dashboard
2. Dashboard shows "Welcome, [First Name]!"
3. User can logout and login again

### Successful Login:
1. Enter credentials → Submit → Redirect to dashboard
2. Dashboard shows user's name
3. All protected pages accessible

### Security:
1. Unauthenticated users redirected to auth
2. Duplicate emails rejected
3. Invalid credentials rejected
4. CSRF protection active

---

## 🚀 Quick Start Testing

1. **Open browser:** http://localhost:8001/
2. **Register new user:** Click "Start Your Journey" → Fill form → Submit
3. **Test dashboard:** Should see personalized welcome
4. **Test logout:** Click logout → Should return to welcome page
5. **Test login:** Click "Access Your Account" → Enter credentials → Submit
6. **Test navigation:** Try accessing different pages

**Happy Testing! 🎉**
