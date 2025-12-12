from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from models.db import db
import logging
import traceback


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

    # Import blueprints here to avoid circular imports
    from blueprints.skincare import skincare_bp

    # Register blueprints
    app.register_blueprint(skincare_bp, url_prefix='/skincare')

    # Create tables
    with app.app_context():
        try:
            # Import models here to ensure they're registered
            from models import user, skin_profile, product, recommendation
            db.create_all()
            logger.info("Database tables created successfully")

            # Create a test user if it doesn't exist
            from models.user import User
            test_user = User.query.get(1)
            if not test_user:
                test_user = User(id=1, email="test@example.com", name="Test User")
                db.session.add(test_user)
                db.session.commit()
                logger.info("Created test user with ID: 1")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            logger.error(traceback.format_exc())

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'message': 'PRRA API is running'}), 200

    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    @app.route('/test')
    def test_page():
        return send_from_directory('static', 'test.html')

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
    print("🧪 Test Page: http://localhost:5001/test")
    print("❤️  Health: http://localhost:5001/health")
    print("=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5001, debug=True)