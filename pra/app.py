from flask import Flask, send_from_directory, jsonify, render_template, request, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from pra.config import Config
from pra.models.db import db
import logging
import traceback
from dotenv import load_dotenv
import os
import re
from pra.blueprints.routine_builder import routine_builder_bp

# Load environment variables from .env file
load_dotenv()

# Initialize Flask-Login
login_manager = LoginManager()
#testing

def create_app(config_class=Config):
    #building a new house with a static storage room
    app = Flask(__name__, static_folder='static')
    #configure the house according to the blueprint
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

    # Initialize database connects db object to flask app 
    db.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth_page'
    login_manager.login_message = 'Please log in to access this page.'

    # use this function to load users 
    @login_manager.user_loader
    def load_user(user_id):
        from pra.models.user import User
        return User.query.get(int(user_id))

    # Import blueprints here to avoid circular imports
    from pra.blueprints.skincare import skincare_bp
    from pra.blueprints.deals import deals_bp
    from pra.blueprints.community import community_bp
    from pra.routes.analytics_routes import analytics_bp

    # Register blueprints
    app.register_blueprint(skincare_bp, url_prefix='/skincare')
    app.register_blueprint(deals_bp, url_prefix='/deals')
    app.register_blueprint(community_bp, url_prefix='/community')
    app.register_blueprint(routine_builder_bp)
    app.register_blueprint(analytics_bp)

    from pra.middleware.analytics_middleware import AnalyticsMiddleware
    AnalyticsMiddleware(app)

    # Create tables
    with app.app_context():
        try:
            # Import models here to ensure they're registered
            from pra.models import user, skin_profile, product, recommendation, routine, community, analytics
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
        # If user is logged in, redirect to dashboard
        if current_user.is_authenticated:
            if current_user.email.endswith('@admin.com'):
                return redirect(url_for('analytics.dashboard'))
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard - shows routine, wardrobe, shopping lists"""
        from pra.models.routine import SavedRoutine, ShoppingList
        from pra.models.product import Wardrobe
        from datetime import datetime
        import json

        # Get user's stats
        routine = SavedRoutine.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).order_by(SavedRoutine.updated_at.desc()).first()

        wardrobe_count = Wardrobe.query.filter_by(user_id=current_user.id).count()
        shopping_lists = ShoppingList.query.filter_by(user_id=current_user.id).all()
        shopping_list_count = sum(len(sl.shopping_list_items) for sl in shopping_lists)

        # Calculate estimated savings (placeholder)
        estimated_savings = 0.0

        stats = {
            'routine_count': 1 if routine else 0,
            'wardrobe_count': wardrobe_count,
            'shopping_list_count': shopping_list_count,
            'estimated_savings': estimated_savings
        }

        # Prepare routine data if exists
        routine_data = None
        if routine:
            routine_json = json.loads(routine.routine_data)
            am_steps = len(routine_json.get('AM', []))
            pm_steps = len(routine_json.get('PM', []))

            # Calculate time ago
            time_diff = datetime.utcnow() - routine.updated_at
            if time_diff.days == 0:
                updated_ago = "today"
            elif time_diff.days == 1:
                updated_ago = "yesterday"
            else:
                updated_ago = f"{time_diff.days} days ago"

            routine_data = {
                'skin_type': routine.skin_type,
                'concerns': json.loads(routine.concerns),
                'am_steps': am_steps,
                'pm_steps': pm_steps,
                'updated_ago': updated_ago,
                'session_id': routine.session_id
            }

        return render_template('dashboard.html',
                             user=current_user,
                             stats=stats,
                             routine=routine_data)

    @app.route('/test')
    def test_page():
        return send_from_directory('static', 'test.html')

    @app.route('/auth')
    def auth_page():
        return render_template('auth.html')

    @app.route('/todays-deals')
    def todays_deals():
        """Today's deals page with current sales"""
        return render_template('todays_deals.html')

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
            from pra.models.user import User
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
            session.permanent = True
            logger.info(f"User logged in: {user.email}")

            redirect_url = '/'
            if user.email.endswith('@admin.com'):
                redirect_url = '/analytics/dashboard'

            return jsonify({
                'success': True,
                'message': f'Welcome back, {user.name}!',
                'redirect': redirect_url,
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
            from pra.models.user import User
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
            session.permanent = True
            logger.info(f"New user created and logged in: {new_user.email}")

            return jsonify({
                'success': True,
                'message': f'Welcome, {new_user.name}! Your account has been created.',
                'redirect': '/',
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

    @app.route('/wardrobe')
    @login_required
    def wardrobe():
        """User's product wardrobe/collection"""
        from pra.models.product import Wardrobe

        products = Wardrobe.query.filter_by(user_id=current_user.id).order_by(Wardrobe.created_at.desc()).all()

        # Count by status
        own_count = sum(1 for p in products if p.status == 'own')
        want_count = sum(1 for p in products if p.status == 'want_to_try')
        used_count = sum(1 for p in products if p.status == 'used_to_own')

        return render_template('wardrobe.html',
                             products=products,
                             total_count=len(products),
                             own_count=own_count,
                             want_count=want_count,
                             used_count=used_count)

    @app.route('/api/wardrobe', methods=['POST'])
    @login_required
    def add_to_wardrobe():
        """Add product to user's wardrobe"""
        from pra.models.product import Wardrobe

        try:
            data = request.get_json()

            wardrobe_item = Wardrobe(
                user_id=current_user.id,
                product_name=data.get('product_name'),
                brand=data.get('brand'),
                category=data.get('category'),
                status=data.get('status', 'want_to_try'),
                price=data.get('price'),
                url=data.get('url'),
                image_url=data.get('image_url'),
                user_rating=data.get('user_rating'),
                notes=data.get('notes')
            )

            db.session.add(wardrobe_item)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Product added to wardrobe',
                'product': wardrobe_item.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding to wardrobe: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to add product'
            }), 500

    @app.route('/api/wardrobe/<int:item_id>', methods=['GET'])
    @login_required
    def get_wardrobe_item(item_id):
        """Get single wardrobe item"""
        from pra.models.product import Wardrobe

        item = Wardrobe.query.filter_by(id=item_id, user_id=current_user.id).first()

        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404

        return jsonify({
            'success': True,
            'product': item.to_dict()
        }), 200

    @app.route('/api/wardrobe/<int:item_id>', methods=['PUT'])
    @login_required
    def update_wardrobe_item(item_id):
        """Update wardrobe item"""
        from pra.models.product import Wardrobe

        try:
            item = Wardrobe.query.filter_by(id=item_id, user_id=current_user.id).first()

            if not item:
                return jsonify({'success': False, 'error': 'Item not found'}), 404

            data = request.get_json()

            item.product_name = data.get('product_name', item.product_name)
            item.brand = data.get('brand', item.brand)
            item.category = data.get('category', item.category)
            item.status = data.get('status', item.status)
            item.price = data.get('price', item.price)
            item.url = data.get('url', item.url)
            item.image_url = data.get('image_url', item.image_url)
            item.user_rating = data.get('user_rating', item.user_rating)
            item.notes = data.get('notes', item.notes)

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Product updated',
                'product': item.to_dict()
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating wardrobe item: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to update product'
            }), 500

    @app.route('/api/wardrobe/<int:item_id>', methods=['DELETE'])
    @login_required
    def remove_from_wardrobe(item_id):
        """Remove product from wardrobe"""
        from pra.models.product import Wardrobe

        try:
            item = Wardrobe.query.filter_by(id=item_id, user_id=current_user.id).first()

            if not item:
                return jsonify({'success': False, 'error': 'Item not found'}), 404

            db.session.delete(item)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Product removed from wardrobe'
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing from wardrobe: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to remove product'
            }), 500

    @app.route('/shopping-lists')
    @login_required
    def shopping_lists():
        """User's shopping lists page"""
        from pra.models.routine import ShoppingList

        lists = ShoppingList.query.filter_by(user_id=current_user.id).order_by(ShoppingList.created_at.desc()).all()

        return render_template('shopping_lists.html',
                             user=current_user,
                             shopping_lists=lists)

    @app.route('/settings')
    @login_required
    def settings():
        """User settings page"""
        return render_template('settings.html', user=current_user)

    @app.route('/api/add-to-shopping-list', methods=['POST'])
    @login_required
    def add_to_shopping_list():
        """Add product to user's shopping list"""
        from pra.models.routine import ShoppingList, ShoppingListItem
        from pra.models.product import Product

        try:
            data = request.get_json()

            # Get or create default shopping list for user
            shopping_list = ShoppingList.query.filter_by(
                user_id=current_user.id
            ).order_by(ShoppingList.created_at.desc()).first()

            if not shopping_list:
                shopping_list = ShoppingList(
                    user_id=current_user.id,
                    name="My Shopping List"
                )
                db.session.add(shopping_list)
                db.session.flush()  # Get the ID

            # Check if product already exists in products table
            product = Product.query.filter_by(
                name=data.get('product_name'),
                brand=data.get('brand')
            ).first()

            if not product:
                # Create new product
                product = Product(
                    name=data.get('product_name'),
                    brand=data.get('brand'),
                    price=data.get('price'),
                    url=data.get('url'),
                    image_url=data.get('image_url'),
                    source='user_added'
                )
                db.session.add(product)
                db.session.flush()  # Get the ID

            # Check if product already in shopping list
            existing_item = ShoppingListItem.query.filter_by(
                shopping_list_id=shopping_list.id,
                product_id=product.id
            ).first()

            if existing_item:
                return jsonify({
                    'success': True,
                    'message': 'Product already in your shopping list',
                    'shopping_list_id': shopping_list.id
                }), 200

            # Add to shopping list
            list_item = ShoppingListItem(
                shopping_list_id=shopping_list.id,
                product_id=product.id,
                is_affordable_option=data.get('is_affordable_option', True)
            )

            db.session.add(list_item)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': f'Added {product.name} to your shopping list!',
                'shopping_list_id': shopping_list.id,
                'product_id': product.id
            }), 201

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding to shopping list: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': 'Failed to add product to shopping list'
            }), 500

    @app.route('/api/shopping-list-item/<int:item_id>', methods=['PUT'])
    @login_required
    def update_shopping_list_item(item_id):
        """Update shopping list item (e.g., mark as purchased)"""
        from pra.models.routine import ShoppingListItem, ShoppingList

        try:
            # Verify item belongs to user
            item = ShoppingListItem.query.join(ShoppingList).filter(
                ShoppingListItem.id == item_id,
                ShoppingList.user_id == current_user.id
            ).first()

            if not item:
                return jsonify({'success': False, 'error': 'Item not found'}), 404

            data = request.get_json()

            if 'is_purchased' in data:
                item.is_purchased = data['is_purchased']

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Item updated successfully'
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating shopping list item: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to update item'
            }), 500

    @app.route('/api/shopping-list-item/<int:item_id>', methods=['DELETE'])
    @login_required
    def remove_shopping_list_item(item_id):
        """Remove item from shopping list"""
        from pra.models.routine import ShoppingListItem, ShoppingList

        try:
            # Verify item belongs to user
            item = ShoppingListItem.query.join(ShoppingList).filter(
                ShoppingListItem.id == item_id,
                ShoppingList.user_id == current_user.id
            ).first()

            if not item:
                return jsonify({'success': False, 'error': 'Item not found'}), 404

            db.session.delete(item)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Item removed from shopping list'
            }), 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing shopping list item: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to remove item'
            }), 500

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
