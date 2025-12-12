import os
from datetime import timedelta


class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database - Use SQLite for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///prra.db'  # Changed to SQLite
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQL_ECHO', 'False') == 'True'

    # Redis (optional - for future caching)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # External API Keys (placeholders)
    SEPHORA_API_KEY = os.environ.get('SEPHORA_API_KEY', '')
    AMAZON_API_KEY = os.environ.get('AMAZON_API_KEY', '')
    SKINCARE_API_KEY = os.environ.get('SKINCARE_API_KEY', '')

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