# Authentication Quick Start Guide

## Get Started in 3 Steps

### Step 1: Start the App
```bash
cd pra
python app.py
```

### Step 2: Open Your Browser
Navigate to: **http://localhost:5001/auth**

### Step 3: Create Your Account
Click "Create an Account" and fill in your details!

---

## What You'll See

### 1. Welcome Screen
When you first visit `/auth`, you'll see:
- Beautiful purple gradient background
- Clean white card with "Welcome to PRA" heading
- Subtitle: "Your personalized shopping and skincare companion"
- Two buttons:
  - **"Sign In"** - For existing users
  - **"Create an Account"** - For new users

### 2. Sign In Modal (Click "Sign In" button)
A modal pops up with:
- **Tabs**: Toggle between "Sign In" and "Create Account"
- **Email field**: Your email address
- **Password field**: Your password
- **Forgot password?** link (coming soon)
- **Social login buttons**: Google and Apple (UI ready for OAuth)
- Close button (X) in top right

### 3. Sign Up Modal (Click "Create an Account" button)
A modal pops up with:
- **Tabs**: Toggle between "Sign In" and "Create Account"
- **Name field**: Your full name
- **Email field**: Your email address
- **Password field**: Minimum 8 characters
- **Confirm password field**: Must match password
- **Terms agreement**: Links to Terms of Service and Privacy Policy
- **Social signup buttons**: Google and Apple

---

## Color Scheme

The design uses a modern, professional color palette:

- **Primary Purple**: `#6366F1` - Buttons and accents
- **Gradient Background**: Purple to violet (`#667eea` to `#764ba2`)
- **Text Primary**: `#1F2937` - Dark gray for readability
- **Success Green**: `#10B981` - Success messages
- **Error Red**: `#EF4444` - Error messages
- **White**: `#FFFFFF` - Cards and modals

---

## Form Validation

### Login Form
- ✅ Email must be valid format
- ✅ Password is required
- ❌ Shows error if credentials are invalid

### Signup Form
- ✅ Name is required
- ✅ Email must be valid format
- ✅ Password must be at least 8 characters
- ✅ Passwords must match
- ❌ Shows error if email already exists

---

## Success Flow

### After Successful Signup:
1. Green success message appears
2. "Account created successfully! Redirecting..."
3. Auto-login happens
4. Redirects to `/deals` page
5. You're now authenticated!

### After Successful Login:
1. Green success message appears
2. "Login successful! Redirecting..."
3. Session is created with "Remember Me"
4. Redirects to `/deals` page
5. You stay logged in for 30 days!

---

## Error Handling

### Common Errors:

**"An account with this email already exists"**
- This email is registered - try logging in instead

**"Invalid email or password"**
- Check your credentials and try again

**"Passwords do not match"**
- Make sure both password fields are identical

**"Password must be at least 8 characters long"**
- Choose a longer password for security

---

## Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Enter**: Submit form
- **Escape**: Close modal
- **Arrow Keys**: Navigate buttons

---

## Mobile Experience

The auth pages are fully responsive:
- **Desktop**: Full-size modal with tabs
- **Tablet**: Optimized spacing and button sizes
- **Mobile**: Stack social buttons vertically, larger tap targets
- **All sizes**: Touch-friendly, no zoom on iOS

---

## Testing Tips

### Test Account Creation:
```bash
curl -X POST http://localhost:5001/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test Login:
```bash
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Check Current User:
```bash
curl http://localhost:5001/current-user
```

---

## Next Steps After Login

Once logged in, you can:
1. Browse deals at `/deals`
2. Access your profile (if you add a profile page)
3. Save favorite products (future feature)
4. Track your shopping journey

To protect any route with authentication:
```python
from flask_login import login_required

@app.route('/my-page')
@login_required
def my_page():
    return "Protected content!"
```

---

## Customization Quick Tips

### Change Primary Color:
Edit `pra/static/css/auth.css` line 13:
```css
--primary: #YOUR_COLOR;
```

### Change Welcome Message:
Edit `pra/templates/auth.html` line 14:
```html
<h1 class="welcome-title">Your Custom Title</h1>
```

### Change Redirect URL:
Edit `pra/app.py` line 141:
```python
'redirect': '/your-page'
```

---

## That's It!

You now have a beautiful, secure authentication system. Enjoy! 🎉

For more details, see:
- [AUTH_SETUP.md](AUTH_SETUP.md) - Complete setup guide
- [AUTHENTICATION_COMPLETE.md](AUTHENTICATION_COMPLETE.md) - Feature overview
