from flask import Flask, send_from_directory, jsonify, render_template, request, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from pra.config import Config
from pra.models.db import db
import logging
import traceback
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()

# Initialize Flask-Login
login_manager = LoginManager()
#testing

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)

    # Enable CORS for all routes
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Setup logging
    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth_page'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        from pra.models.user import User
        return User.query.get(int(user_id))

    # Import blueprints here to avoid circular imports
    from pra.blueprints.skincare import skincare_bp
    from pra.blueprints.deals import deals_bp

    # Register blueprints
    app.register_blueprint(skincare_bp, url_prefix='/skincare')
    app.register_blueprint(deals_bp, url_prefix='/deals')

    # Create tables
    with app.app_context():
        try:
            # Import models here to ensure they're registered
            from pra.models import user, skin_profile, product, recommendation
            db.create_all()
            logger.info("Database tables created successfully")

            # Create a test user if it doesn't exist
            from pra.models.user import User
            test_user = User.query.filter_by(email="test@example.com").first()
            if not test_user:
                test_user = User(email="test@example.com", name="Test User")
                test_user.set_password("password123")
                db.session.add(test_user)
                db.session.commit()
                logger.info(f"Created test user: {test_user.email}")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            logger.error(traceback.format_exc())

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'message': 'PRRA API is running'}), 200

    @app.route('/')
    def index():
        """Main landing page with deals, auth, and recommendations"""
        return render_template('index.html')

    @app.route('/test')
    def test_page():
        return send_from_directory('static', 'test.html')

    @app.route('/auth')
    def auth_page():
        return render_template('auth.html')

    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')

            # Validate input
            if not email or not password:
                return jsonify({
                    'success': False,
                    'error': 'Email and password are required'
                }), 400

            # Email format validation
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                return jsonify({
                    'success': False,
                    'error': 'Invalid email format'
                }), 400

            # Find user
            from models.user import User
            user = User.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                return jsonify({
                    'success': False,
                    'error': 'Invalid email or password'
                }), 401

            if not user.is_active:
                return jsonify({
                    'success': False,
                    'error': 'Your account has been deactivated'
                }), 403

            # Login user
            login_user(user, remember=True)
            logger.info(f"User logged in: {user.email}")

            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'redirect': '/deals',
                'user': user.to_dict()
            }), 200

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': 'An error occurred during login. Please try again.'
            }), 500

    @app.route('/signup', methods=['POST'])
    def signup():
        try:
            data = request.get_json()
            name = data.get('name', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')

            # Validate input
            if not name or not email or not password:
                return jsonify({
                    'success': False,
                    'error': 'Name, email, and password are required'
                }), 400

            # Email format validation
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                return jsonify({
                    'success': False,
                    'error': 'Invalid email format'
                }), 400

            # Password strength validation
            if len(password) < 8:
                return jsonify({
                    'success': False,
                    'error': 'Password must be at least 8 characters long'
                }), 400

            # Check if user already exists
            from models.user import User
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({
                    'success': False,
                    'error': 'An account with this email already exists'
                }), 409

            # Create new user
            new_user = User(email=email, name=name)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            # Auto-login the user
            login_user(new_user, remember=True)
            logger.info(f"New user created and logged in: {new_user.email}")

            return jsonify({
                'success': True,
                'message': 'Account created successfully!',
                'redirect': '/deals',
                'user': new_user.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Signup error: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': 'An error occurred during signup. Please try again.'
            }), 500

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        try:
            user_email = current_user.email
            logout_user()
            logger.info(f"User logged out: {user_email}")
            return jsonify({
                'success': True,
                'message': 'Logged out successfully',
                'redirect': '/auth'
            }), 200
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'An error occurred during logout'
            }), 500

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

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found', 'message': str(e)}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    print("\n" + "=" * 60)
    print("🚀 PRRA Server Starting...")
    print("=" * 60)
    print("📍 Main App: http://localhost:5001")
    print("🔐 Auth Page: http://localhost:5001/auth")
    print("💰 Deals Finder: http://localhost:5001/deals")
    print("🧪 Test Page: http://localhost:5001/test")
    print("❤️  Health: http://localhost:5001/health")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5001, debug=True)