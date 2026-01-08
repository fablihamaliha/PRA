# Complete Line-by-Line Explanation of app.py

**A Beginner's Guide to Understanding Your Flask Application**

---

## Table of Contents

1. [Imports - Bringing in Tools](#section-1-imports)
2. [Initial Setup](#section-2-initial-setup)
3. [Application Factory](#section-3-application-factory)
4. [CORS Setup](#section-4-cors-setup)
5. [Logging Setup](#section-5-logging-setup)
6. [Database Initialization](#section-6-database-initialization)
7. [Login Manager Setup](#section-7-login-manager-setup)
8. [Blueprints](#section-8-blueprints)
9. [Database Table Creation](#section-9-database-table-creation)
10. [Basic Routes](#section-10-basic-routes)
11. [Login Endpoint](#section-11-login-endpoint)
12. [Signup Endpoint](#section-12-signup-endpoint)
13. [Logout Endpoint](#section-13-logout-endpoint)
14. [Current User Endpoint](#section-14-current-user-endpoint)
15. [Error Handlers](#section-15-error-handlers)
16. [Return the App](#section-16-return-the-app)
17. [Running the App](#section-17-running-the-app)

---

## SECTION 1: Imports (Lines 1-10) - Bringing in Tools {#section-1-imports}

### Line 1: `from flask import Flask, send_from_directory, jsonify, render_template, request, session`

Think of this like opening your toolbox. You're bringing in tools from Flask:

- **`Flask`**: The main tool that creates your web application (like the blueprint of a house)
- **`send_from_directory`**: Sends files from a folder (like handing someone a document)
- **`jsonify`**: Converts Python data into JSON format (the language browsers understand)
- **`render_template`**: Loads HTML files and shows them to users (like showing a webpage)
- **`request`**: Receives data sent by users (like reading a letter someone sent you)
- **`session`**: Remembers information about a user while they browse (like a notepad)

### Line 2: `from flask_cors import CORS`

**CORS** = Cross-Origin Resource Sharing

- Allows your frontend (JavaScript) to talk to your backend (Flask API)
- Without this, browsers block requests for security reasons
- Think of it as: "Yes, I trust requests from other websites"

### Line 3: `from flask_login import LoginManager, login_user, logout_user, login_required, current_user`

Tools for handling user logins:

- **`LoginManager`**: The main manager that handles who's logged in
- **`login_user`**: Logs someone in (like giving them a key to the building)
- **`logout_user`**: Logs someone out (taking back the key)
- **`login_required`**: A decorator that says "you must be logged in to access this"
- **`current_user`**: Access information about whoever is currently logged in

### Line 4: `from pra.config import Config`

Imports your configuration settings from `config.py`

- Contains settings like database URL, secret keys, debug mode
- Think of it as your app's settings file

### Line 5: `from pra.models.db import db`

Imports the database object

- `db` is your connection to the database (PostgreSQL or SQLite)
- Allows you to save and retrieve data

### Lines 6-10: Standard Python Libraries

- **Line 6** `import logging`: Records events/errors (like a diary for your app)
- **Line 7** `import traceback`: Shows detailed error information when things crash
- **Line 8** `from dotenv import load_dotenv`: Reads secret keys from `.env` file
- **Line 9** `import os`: Interact with operating system (read files, environment variables)
- **Line 10** `import re`: Regular expressions (pattern matching for text, like email validation)

---

## SECTION 2: Initial Setup (Lines 12-16) {#section-2-initial-setup}

### Lines 12-13: Load Environment Variables

```python
# Load environment variables from .env file
load_dotenv()
```

Reads your `.env` file containing secrets like:

- `SECRET_KEY=your_secret_key`
- `DATABASE_URL=postgresql://...`
- `OPENAI_API_KEY=sk-...`

This keeps secrets out of your code (security best practice)

### Lines 15-16: Initialize Login Manager

```python
# Initialize Flask-Login
login_manager = LoginManager()
```

Creates the login manager object (but doesn't connect it to your app yet - that happens later on line 43)

---

## SECTION 3: Application Factory (Lines 19-259) - The Heart of Your App {#section-3-application-factory}

### Line 19: `def create_app(config_class=Config):`

This is called the **Application Factory Pattern**. Why use a function instead of just creating the app directly?

**Benefits:**

1. You can create multiple apps with different settings (testing, development, production)
2. Cleaner initialization
3. Better for testing

**Parameter:** `config_class=Config` - Defaults to your main Config but can be changed

### Line 20: `app = Flask(__name__, static_folder='static')`

**Creates your Flask application!**

- `__name__`: Tells Flask where to find templates and static files
- `static_folder='static'`: Where CSS, JavaScript, images are stored

Think of this as: "Building a new house with a 'static' storage room"

### Line 21: `app.config.from_object(config_class)`

Loads all settings from your Config class:

- Database URL
- Secret key
- Debug mode
- Log level

Like: "Configure the house according to the blueprint"

---

## SECTION 4: CORS Setup (Lines 23-30) {#section-4-cors-setup}

### Lines 24-30: Enable Cross-Origin Requests

```python
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
```

**Breaking it down:**

- `r"/*"`: Apply to ALL routes (the `/*` means "everything")
- `"origins": "*"`: Accept requests from ANY website (in production, you'd limit this)
- `"methods": [...]`: Allow these HTTP methods (GET = read, POST = create, etc.)
- `"allow_headers": ["Content-Type"]`: Allow Content-Type header (tells server what kind of data is being sent)

**Why?** Your frontend (JavaScript) can now make API calls to your backend without browser blocking them.

---

## SECTION 5: Logging Setup (Lines 32-37) {#section-5-logging-setup}

### Lines 33-36: Configure Logging

```python
logging.basicConfig(
    level=app.config['LOG_LEVEL'],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Sets up your app's logging system:

- **`level`**: How detailed? (DEBUG, INFO, WARNING, ERROR)
- **`format`**: How messages look
  - `%(asctime)s`: Timestamp (when it happened)
  - `%(name)s`: Logger name (which part of the app)
  - `%(levelname)s`: Severity (INFO, ERROR, etc.)
  - `%(message)s`: The actual message

**Example output:**

```
2026-01-05 10:30:45 - pra.app - INFO - User logged in: test@example.com
```

### Line 37: `logger = logging.getLogger(__name__)`

Creates a logger specifically for this file (`app.py`)

---

## SECTION 6: Database Initialization (Line 40) {#section-6-database-initialization}

### Line 40: `db.init_app(app)`

Connects your database object to your Flask app

- Now `db` knows about your app's configuration (database URL, etc.)
- Think of it as: "Plugging the database into the app"

---

## SECTION 7: Login Manager Setup (Lines 42-50) {#section-7-login-manager-setup}

### Line 43: `login_manager.init_app(app)`

Connects the login manager to your app (like installing a security system)

### Line 44: `login_manager.login_view = 'auth_page'`

If someone tries to access a protected page without logging in, redirect them to `auth_page` (your login page at `/auth`)

### Line 45: `login_manager.login_message = 'Please log in to access this page.'`

The message shown when they get redirected

### Lines 47-50: User Loader Function

```python
@login_manager.user_loader
def load_user(user_id):
    from pra.models.user import User
    return User.query.get(int(user_id))
```

**What this does:**

- Flask-Login stores the user's ID in a cookie
- When they visit your site, Flask-Login calls this function
- It retrieves the full User object from the database using that ID
- Now you can access `current_user` anywhere in your app

**The `@login_manager.user_loader` decorator** tells Flask-Login: "Use this function to load users"

---

## SECTION 8: Blueprints (Lines 52-58) - Organizing Routes {#section-8-blueprints}

### Lines 53-54: Import Blueprints

```python
from pra.blueprints.skincare import skincare_bp
from pra.blueprints.deals import deals_bp
```

**Blueprints** are like mini-apps within your main app:

- `skincare_bp`: Handles `/skincare/*` routes (quiz, recommendations)
- `deals_bp`: Handles `/deals/*` routes (deal finder)

**Why use blueprints?** Keeps your code organized instead of having 100 routes in one file

### Lines 57-58: Register Blueprints

```python
app.register_blueprint(skincare_bp, url_prefix='/skincare')
app.register_blueprint(deals_bp, url_prefix='/deals')
```

Tells Flask: "Hey, use these blueprints and add `/skincare` or `/deals` to the beginning of their routes"

**Example:**

- Route in `skincare_bp`: `@skincare_bp.route('/quiz')`
- Final URL: `http://localhost:5001/skincare/quiz`

---

## SECTION 9: Database Table Creation (Lines 60-79) {#section-9-database-table-creation}

### Line 61: `with app.app_context():`

Creates an **application context**. Think of it as: "I'm about to do Flask stuff, so Flask needs to know which app I'm talking about"

### Lines 62-66: Create Database Tables

```python
try:
    from pra.models import user, skin_profile, product, recommendation
    db.create_all()
    logger.info("Database tables created successfully")
```

- **Import models**: Imports your database models (User, SkinProfile, etc.)
- **`db.create_all()`**: Creates all database tables if they don't exist
  - Looks at your models and creates tables: `users`, `skin_profiles`, `products`, etc.

### Lines 68-76: Create Test User

```python
from pra.models.user import User
test_user = User.query.filter_by(email="test@example.com").first()
if not test_user:
    test_user = User(email="test@example.com", name="Test User")
    test_user.set_password("password123")
    db.session.add(test_user)
    db.session.commit()
    logger.info(f"Created test user: {test_user.email}")
```

**What happens here:**

1. Check if test user exists: `User.query.filter_by(email="test@example.com").first()`
2. If not, create one:
   - Email: `test@example.com`
   - Password: `password123` (hashed for security)
3. Add to database: `db.session.add(test_user)`
4. Save changes: `db.session.commit()`

**Why?** So you can test login without creating an account manually

### Lines 77-79: Error Handling

```python
except Exception as e:
    logger.error(f"Database initialization error: {str(e)}")
    logger.error(traceback.format_exc())
```

If something goes wrong, log the error instead of crashing

---

## SECTION 10: Basic Routes (Lines 81-96) {#section-10-basic-routes}

### Lines 81-83: Health Check Route

```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'PRRA API is running'}), 200
```

**Purpose:** Check if your app is running (used by Docker health checks)

**Response:**

```json
{
  "status": "healthy",
  "message": "PRRA API is running"
}
```

The `200` is the HTTP status code (200 = OK)

### Lines 85-88: Home Page

```python
@app.route('/')
def index():
    """Main landing page with deals, auth, and recommendations"""
    return render_template('index.html')
```

When someone visits `http://localhost:5001/`, show them `index.html`

### Lines 90-92: Test Page

```python
@app.route('/test')
def test_page():
    return send_from_directory('static', 'test.html')
```

Serves `test.html` from the `static` folder (for testing purposes)

### Lines 94-96: Auth Page

```python
@app.route('/auth')
def auth_page():
    return render_template('auth.html')
```

Shows the login/signup page at `http://localhost:5001/auth`

---

## SECTION 11: Login Endpoint (Lines 98-153) - How Users Log In {#section-11-login-endpoint}

### Line 98: `@app.route('/login', methods=['POST'])`

Defines a route that ONLY accepts POST requests (form submissions)

- GET = retrieve data
- POST = submit data

### Lines 99-103: Extract Data from Request

```python
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
```

**Breaking it down:**

- `request.get_json()`: Gets JSON data sent from the frontend
  - Example: `{"email": "user@example.com", "password": "secret123"}`
- `data.get('email', '')`: Gets the email, defaults to empty string if missing
- `.strip()`: Removes extra spaces (`" user@example.com "` → `"user@example.com"`)
- `.lower()`: Makes it lowercase (`"USER@EXAMPLE.COM"` → `"user@example.com"`)

### Lines 105-110: Validate Required Fields

```python
if not email or not password:
    return jsonify({
        'success': False,
        'error': 'Email and password are required'
    }), 400
```

If email or password is empty, return an error with HTTP status 400 (Bad Request)

### Lines 112-118: Validate Email Format

```python
email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
if not re.match(email_regex, email):
    return jsonify({
        'success': False,
        'error': 'Invalid email format'
    }), 400
```

Uses regex (pattern matching) to check if email looks valid:

- Must have `@` symbol
- Must have domain (`.com`, `.org`, etc.)
- Example valid: `user@example.com`
- Example invalid: `notanemail`

### Lines 120-122: Find User in Database

```python
from models.user import User
user = User.query.filter_by(email=email).first()
```

Searches the database for a user with that email:

- `User.query.filter_by(email=email)`: SQL equivalent: `SELECT * FROM users WHERE email = 'user@example.com'`
- `.first()`: Gets the first result (or `None` if not found)

### Lines 124-128: Check Password

```python
if not user or not user.check_password(password):
    return jsonify({
        'success': False,
        'error': 'Invalid email or password'
    }), 401
```

Two checks:

1. Does user exist? (`not user`)
2. Is password correct? (`not user.check_password(password)`)
   - `check_password()` compares the hashed password (secure)

If either fails, return error 401 (Unauthorized)

### Lines 130-134: Check if Account is Active

```python
if not user.is_active:
    return jsonify({
        'success': False,
        'error': 'Your account has been deactivated'
    }), 403
```

Status 403 = Forbidden (user exists but can't access)

### Lines 136-138: Log User In

```python
login_user(user, remember=True)
logger.info(f"User logged in: {user.email}")
```

- `login_user(user, remember=True)`:
  - Creates a session cookie
  - `remember=True`: Cookie persists even after browser closes
- `logger.info(...)`: Logs this event

### Lines 140-145: Return Success Response

```python
return jsonify({
    'success': True,
    'message': 'Login successful!',
    'redirect': '/deals',
    'user': user.to_dict()
}), 200
```

Sends back:

- Success status
- Message
- Where to redirect (`/deals` page)
- User data (from `to_dict()` method in User model)
- Status 200 (OK)

### Lines 147-153: Error Handling

```python
except Exception as e:
    logger.error(f"Login error: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'success': False,
        'error': 'An error occurred during login. Please try again.'
    }), 500
```

If ANYTHING goes wrong (database error, etc.):

- Log the full error
- Return generic error message (don't expose internal details)
- Status 500 (Internal Server Error)

---

## SECTION 12: Signup Endpoint (Lines 155-219) - Creating New Accounts {#section-12-signup-endpoint}

The signup function is very similar to login, so I'll highlight the differences:

### Lines 158-161: Extract Data

```python
data = request.get_json()
name = data.get('name', '').strip()
email = data.get('email', '').strip().lower()
password = data.get('password', '')
```

Gets name, email, AND password (login only needs email + password)

### Lines 163-168: Validate All Three Fields

```python
if not name or not email or not password:
    return jsonify({
        'success': False,
        'error': 'Name, email, and password are required'
    }), 400
```

### Lines 170-176: Email Format Validation

```python
email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
if not re.match(email_regex, email):
    return jsonify({
        'success': False,
        'error': 'Invalid email format'
    }), 400
```

Same email validation as login

### Lines 178-183: Password Strength Check

```python
if len(password) < 8:
    return jsonify({
        'success': False,
        'error': 'Password must be at least 8 characters long'
    }), 400
```

Ensures password is at least 8 characters (basic security)

### Lines 185-192: Check if User Already Exists

```python
from models.user import User
existing_user = User.query.filter_by(email=email).first()
if existing_user:
    return jsonify({
        'success': False,
        'error': 'An account with this email already exists'
    }), 409
```

Status 409 = Conflict (resource already exists)

### Lines 194-199: Create New User

```python
new_user = User(email=email, name=name)
new_user.set_password(password)

db.session.add(new_user)
db.session.commit()
```

**Step by step:**

1. Create User object: `User(email=email, name=name)`
2. Hash the password: `set_password(password)` (NEVER store passwords in plain text!)
3. Add to database session: `db.session.add(new_user)`
4. Save to database: `db.session.commit()`

**Database session?** Think of it like a shopping cart - you add items, then "checkout" with `commit()`

### Lines 201-203: Auto-Login

```python
login_user(new_user, remember=True)
logger.info(f"New user created and logged in: {new_user.email}")
```

After signup, automatically log them in (better user experience)

### Lines 205-210: Return Success Response

```python
return jsonify({
    'success': True,
    'message': 'Account created successfully!',
    'redirect': '/deals',
    'user': new_user.to_dict()
}), 201
```

Status 201 = Created (new resource was successfully created)

### Lines 212-219: Error Handling with Rollback

```python
except Exception as e:
    db.session.rollback()
    logger.error(f"Signup error: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'success': False,
        'error': 'An error occurred during signup. Please try again.'
    }), 500
```

If an error occurs AFTER adding to session, `rollback()` undoes the changes (prevents corrupted data)

---

## SECTION 13: Logout Endpoint (Lines 221-238) {#section-13-logout-endpoint}

### Lines 221-222: Route with Login Required

```python
@app.route('/logout', methods=['POST'])
@login_required
def logout():
```

`@login_required`: Only logged-in users can access this route

### Lines 224-227: Logout Logic

```python
try:
    user_email = current_user.email
    logout_user()
    logger.info(f"User logged out: {user_email}")
```

- Save email before logout (for logging)
- `logout_user()`: Removes the session cookie
- Log the event

### Lines 228-232: Return Success Response

```python
return jsonify({
    'success': True,
    'message': 'Logged out successfully',
    'redirect': '/auth'
}), 200
```

Redirect to auth page after logout

### Lines 233-238: Error Handling

```python
except Exception as e:
    logger.error(f"Logout error: {str(e)}")
    return jsonify({
        'success': False,
        'error': 'An error occurred during logout'
    }), 500
```

---

## SECTION 14: Current User Endpoint (Lines 240-249) {#section-14-current-user-endpoint}

### Lines 240-249: Get Current User Info

```python
@app.route('/current-user')
def current_user_info():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        }), 200
    return jsonify({
        'authenticated': False
    }), 200
```

**Purpose:** Frontend calls this to check if someone is logged in

**If logged in:**

```json
{
  "authenticated": true,
  "user": {"email": "user@example.com", "name": "John"}
}
```

**If NOT logged in:**

```json
{
  "authenticated": false
}
```

---

## SECTION 15: Error Handlers (Lines 251-257) {#section-15-error-handlers}

### Lines 251-253: 404 Not Found Handler

```python
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found', 'message': str(e)}), 404
```

If someone visits a URL that doesn't exist (e.g., `/nonexistent`), return this JSON instead of an ugly error page

### Lines 255-257: 500 Internal Server Error Handler

```python
@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
```

If something crashes in your app, return a clean JSON error

---

## SECTION 16: Return the App (Line 259) {#section-16-return-the-app}

### Line 259: `return app`

The `create_app()` function returns the fully configured Flask app object

Now it can be used like:

```python
app = create_app()
app.run()
```

---

## SECTION 17: Running the App (Lines 262-274) - The Startup Script {#section-17-running-the-app}

### Line 262: `if __name__ == '__main__':`

**What does this mean?**

This code ONLY runs if you execute this file directly:

```bash
python pra/app.py
```

It does NOT run when you import it:

```python
from pra.app import create_app  # The if block doesn't run
```

### Line 263: `app = create_app()`

Creates the app using the factory function

### Lines 264-272: Pretty Startup Message

```python
print("\n" + "=" * 60)
print("🚀 PRRA Server Starting...")
print("=" * 60)
print("📍 Main App: http://localhost:5001")
print("🔐 Auth Page: http://localhost:5001/auth")
print("💰 Deals Finder: http://localhost:5001/deals")
print("🧪 Test Page: http://localhost:5001/test")
print("❤️  Health: http://localhost:5001/health")
print("=" * 60 + "\n")
```

Prints a nice banner showing all available URLs when the app starts:

```
============================================================
🚀 PRRA Server Starting...
============================================================
📍 Main App: http://localhost:5001
🔐 Auth Page: http://localhost:5001/auth
💰 Deals Finder: http://localhost:5001/deals
🧪 Test Page: http://localhost:5001/test
❤️  Health: http://localhost:5001/health
============================================================
```

### Line 274: `app.run(host='0.0.0.0', port=5001, debug=True)`

**Starts the Flask development server!**

- `host='0.0.0.0'`: Accept connections from any IP address (not just localhost)
  - Allows access from other devices on your network
- `port=5001`: Run on port 5001 (default is 5000)
- `debug=True`:
  - Auto-reloads when you change code
  - Shows detailed error pages
  - **NEVER use in production!** (security risk)

---

## Summary: What This File Does

1. **Sets up Flask app** with database, login system, CORS
2. **Defines authentication routes**: `/login`, `/signup`, `/logout`
3. **Registers blueprints** for skincare and deals features
4. **Creates database tables** and test user
5. **Handles errors** gracefully with custom error handlers
6. **Provides a factory function** (`create_app()`) for creating the app
7. **Includes a development startup script** for running locally

---

## How It All Connects: User Login Flow

```
User visits http://localhost:5001/auth
         ↓
    Flask receives request
         ↓
    Routes to auth_page() function (line 94)
         ↓
    Renders auth.html template
         ↓
    User fills login form
         ↓
    JavaScript POSTs to /login (line 98)
         ↓
    login() function validates credentials
         ↓
    If valid: login_user() creates session
         ↓
    Returns success + redirect to /deals
         ↓
    Frontend redirects user to deals page
```

---

## Key Concepts Explained

### Application Factory Pattern

Instead of creating the Flask app globally, we use a function (`create_app()`) that creates and configures it. This allows:

- Testing with different configurations
- Running multiple instances
- Cleaner initialization process

### Blueprints

Blueprints organize your routes into logical groups. Instead of having all routes in one file, you can split them:

- `app.py` - Main app and authentication routes
- `skincare_bp` - Skincare-related routes (`/skincare/quiz`, `/skincare/recommend`)
- `deals_bp` - Deal finder routes (`/deals/search`)

### Database Sessions

SQLAlchemy uses sessions like a "staging area":

1. `db.session.add(user)` - Stage the change
2. `db.session.commit()` - Save to database
3. `db.session.rollback()` - Undo if something goes wrong

### HTTP Status Codes

- **200 OK** - Request succeeded
- **201 Created** - New resource created
- **400 Bad Request** - Invalid input
- **401 Unauthorized** - Wrong credentials
- **403 Forbidden** - Not allowed to access
- **404 Not Found** - Resource doesn't exist
- **409 Conflict** - Resource already exists
- **500 Internal Server Error** - Something went wrong on the server

### Password Security

Never store passwords in plain text! Your app uses:

- `set_password(password)` - Hashes the password using bcrypt
- `check_password(password)` - Compares hashed versions

Even if your database is compromised, attackers can't read passwords.

### CORS (Cross-Origin Resource Sharing)

Browsers block requests from one domain to another for security. CORS tells the browser: "It's okay, I trust requests from these sources."

Your app allows requests from anywhere (`"origins": "*"`), which is fine for development but should be restricted in production.

---

## Important Security Notes

1. **Never commit secrets** - Use `.env` file and `.gitignore`
2. **Always hash passwords** - Use `set_password()`, never store plain text
3. **Validate all input** - Check email format, password length, etc.
4. **Use HTTPS in production** - Encrypts data in transit
5. **Set `debug=False` in production** - Debug mode exposes sensitive information
6. **Restrict CORS in production** - Don't allow all origins (`*`)
7. **Use environment-specific configs** - Different settings for dev/prod

---

## Common Debugging Tips

### App won't start?

- Check if port 5001 is already in use
- Verify `.env` file exists with required variables
- Check database connection string

### Login not working?

- Check if user exists in database
- Verify password is being hashed
- Look at browser console for JavaScript errors
- Check server logs for detailed error messages

### 404 errors?

- Verify route is registered (check blueprint registration)
- Check URL matches route exactly (including trailing slashes)
- Make sure template files exist in `templates/` folder

### CORS errors?

- Check browser console for CORS messages
- Verify CORS is configured correctly (lines 24-30)
- Ensure frontend is making requests to correct URL

---

## Next Steps

Now that you understand `app.py`, you can explore:

1. **Models** (`pra/models/`) - How data is structured
2. **Blueprints** (`pra/blueprints/`) - Feature-specific routes
3. **Services** (`pra/services/`) - Business logic
4. **Templates** (`pra/templates/`) - Frontend HTML
5. **Configuration** (`pra/config.py`) - App settings

---

**Created: January 6, 2026**
**File: /Users/maliha/Desktop/PRA/pra/app.py**
**For: PRA (Personal Recommendation Assistant) Project**
