import os
from datetime import timedelta


class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Session configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    # # Database - Use SQLite for local development
  # Database - PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://prra_user:prra_password_123@localhost:5432/prra_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQL_ECHO', 'False') == 'True'
     
    # Redis (optional - for future caching)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # External API Keys (placeholders)
    SEPHORA_API_KEY = os.environ.get('SEPHORA_API_KEY', '')
    AMAZON_API_KEY = os.environ.get('AMAZON_API_KEY', '')
    SKINCARE_API_KEY = os.environ.get('SKINCARE_API_KEY', '')

    # Deal Finder API Keys
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
    GOOGLE_CUSTOM_SEARCH_CX = os.environ.get('GOOGLE_CUSTOM_SEARCH_CX', '')
    WALMART_API_KEY = os.environ.get('WALMART_API_KEY', '')
    TARGET_API_KEY = os.environ.get('TARGET_API_KEY', '')
    BEST_BUY_API_KEY = os.environ.get('BEST_BUY_API_KEY', '')
    AMAZON_ACCESS_KEY = os.environ.get('AMAZON_ACCESS_KEY', '')
    AMAZON_SECRET_KEY = os.environ.get('AMAZON_SECRET_KEY', '')
    AMAZON_ASSOCIATE_TAG = os.environ.get('AMAZON_ASSOCIATE_TAG', '')
    RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '')

    # API Rate Limiting
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100')

    # Recommendation Settings
    MAX_RECOMMENDATIONS = int(os.environ.get('MAX_RECOMMENDATIONS', '3'))
    MIN_PRODUCT_RATING = float(os.environ.get('MIN_PRODUCT_RATING', '3.5'))

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///prra_dev.db'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://prra_user:prra_pass@db:5432/prra_db'
    )


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'