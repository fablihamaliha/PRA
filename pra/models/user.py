from pra.models.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    # Add this to the User model relationships:
    shopping_lists = db.relationship('ShoppingList', back_populates='user', cascade='all, delete-orphan')
    routines = db.relationship('Routine', back_populates='user', cascade='all, delete-orphan')
    visitor_logs = db.relationship('VisitorLog', back_populates='user', cascade='all, delete-orphan')
    security_events = db.relationship('SecurityEvent', back_populates='user', cascade='all, delete-orphan')
    analytics_events = db.relationship('AnalyticsEvent', back_populates='user', cascade='all, delete-orphan')
    saved_routines = db.relationship('SavedRoutine', back_populates='user', cascade='all, delete-orphan')

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    skin_profiles = db.relationship('SkinProfile', back_populates='user', cascade='all, delete-orphan')
    recommendation_sessions = db.relationship('RecommendationSession', back_populates='user',
                                              cascade='all, delete-orphan')
    product_comments = db.relationship('ProductComment', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
