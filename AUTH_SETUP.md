# Authentication Setup Guide

## Overview

Your PRA application now has a fully functional authentication system with modern, beautiful login and signup pages.

## Features

- **Modern UI**: Clean, professional design inspired by popular platforms like Stripe and Notion
- **Secure Authentication**: Password hashing using Werkzeug's secure methods
- **Flask-Login Integration**: Session management with "Remember Me" functionality
- **Input Validation**: Email format validation and password strength requirements
- **Error Handling**: User-friendly error messages for common issues
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Accessibility**: ARIA labels and keyboard navigation support

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The authentication system requires:
- Flask-Login==0.6.3
- Werkzeug==3.0.1
- bcrypt==4.1.2

### 2. Database Migration

Since we added new fields to the User model (`password_hash` and `is_active`), you'll need to:

**Option A: Fresh Start (Development)**
```bash
# Delete the old database
rm pra/prra.db

# Restart the app (it will create a new database automatically)
python pra/app.py
```

**Option B: Migration (If you have existing data)**
If you have important existing users, you'll need to add the new columns manually or use a migration tool like Alembic.

### 3. Run the Application

```bash
cd pra
python app.py
```

The app will start on http://localhost:5001

## Using the Authentication System

### Access the Auth Page

Visit: http://localhost:5001/auth

### Sign Up Flow

1. Click "Create an Account" button
2. Fill in:
   - Full Name
   - Email (must be valid format)
   - Password (minimum 8 characters)
   - Confirm Password
3. Click "Create account"
4. You'll be automatically logged in and redirected to `/deals`

### Login Flow

1. Click "Sign In" button
2. Enter your email and password
3. Click "Log in"
4. You'll be redirected to `/deals`

## API Endpoints

### POST /signup
Create a new user account

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "Account created successfully!",
  "redirect": "/deals",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "created_at": "2025-01-15T10:30:00",
    "is_active": true
  }
}
```

### POST /login
Authenticate an existing user

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful!",
  "redirect": "/deals",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "created_at": "2025-01-15T10:30:00",
    "is_active": true
  }
}
```

### POST /logout
Log out the current user (requires authentication)

**Success Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully",
  "redirect": "/auth"
}
```

### GET /current-user
Get the currently authenticated user

**Authenticated Response (200):**
```json
{
  "authenticated": true,
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    "created_at": "2025-01-15T10:30:00",
    "is_active": true
  }
}
```

**Unauthenticated Response (200):**
```json
{
  "authenticated": false
}
```

## Security Features

1. **Password Hashing**: Passwords are hashed using Werkzeug's `generate_password_hash`
2. **Session Management**: Flask-Login handles secure session cookies
3. **Input Validation**:
   - Email format validation (regex)
   - Password minimum length (8 characters)
   - Duplicate email prevention
4. **CSRF Protection**: Consider adding Flask-WTF for production
5. **HTTPS Ready**: Configure `SESSION_COOKIE_SECURE=True` in production

## Customization

### Changing the Redirect After Login

Edit [app.py:141](pra/app.py#L141) and [app.py:206](pra/app.py#L206):

```python
'redirect': '/your-custom-page'
```

### Modifying Password Requirements

Edit [app.py:177](pra/app.py#L177):

```python
if len(password) < 12:  # Change minimum length
    return jsonify({
        'success': False,
        'error': 'Password must be at least 12 characters long'
    }), 400
```

### Styling Changes

The CSS is located at: [pra/static/css/auth.css](pra/static/css/auth.css)

Key variables to customize:
```css
:root {
    --primary: #6366F1;  /* Primary color */
    --primary-hover: #4F46E5;  /* Hover state */
    --radius: 12px;  /* Border radius */
}
```

## Protecting Routes

To require authentication for a route, use the `@login_required` decorator:

```python
from flask_login import login_required, current_user

@app.route('/protected-page')
@login_required
def protected_page():
    user_name = current_user.name
    return f"Hello, {user_name}!"
```

## Testing

### Test the Signup Flow
```bash
curl -X POST http://localhost:5001/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

### Test the Login Flow
```bash
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

## Troubleshooting

### "An account with this email already exists"
The email is already registered. Try logging in instead or use a different email.

### "Invalid email or password"
Double-check your credentials. Emails are case-insensitive and trimmed automatically.

### Database errors after update
Delete the old database and let the app recreate it:
```bash
rm pra/prra.db
python pra/app.py
```

### Session not persisting
Make sure `SECRET_KEY` is set in your config and doesn't change between restarts.

## Next Steps

Consider adding:
1. **Password Reset**: Email-based password recovery
2. **Email Verification**: Verify user emails before activation
3. **Social Login**: Google/Apple OAuth integration (buttons already in UI)
4. **Two-Factor Authentication**: Extra security layer
5. **Password Strength Meter**: Visual feedback on password strength
6. **Rate Limiting**: Prevent brute force attacks

## Files Modified

- [pra/templates/auth.html](pra/templates/auth.html) - Authentication UI
- [pra/static/css/auth.css](pra/static/css/auth.css) - Styling
- [pra/models/user.py](pra/models/user.py) - User model with password hashing
- [pra/app.py](pra/app.py) - Authentication routes and Flask-Login setup
- [pra/config.py](pra/config.py) - Session configuration
- [requirements.txt](requirements.txt) - New dependencies

Enjoy your new authentication system!
