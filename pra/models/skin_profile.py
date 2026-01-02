from pra.models.db import db
from datetime import datetime
import json


class SkinProfile(db.Model):
    __tablename__ = 'skin_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Profile data
    skin_type = db.Column(db.String(50), nullable=False)  # oily, dry, combination, normal, sensitive
    concerns = db.Column(db.Text)  # JSON string for SQLite compatibility

    # Budget
    budget_min = db.Column(db.Float, nullable=True)
    budget_max = db.Column(db.Float, nullable=True)

    # Ingredients
    preferred_ingredients = db.Column(db.Text)  # JSON string
    avoided_ingredients = db.Column(db.Text)  # JSON string

    # Metadata
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='skin_profiles')
    recommendation_sessions = db.relationship('RecommendationSession', back_populates='skin_profile')

    def __repr__(self):
        return f'<SkinProfile user_id={self.user_id} type={self.skin_type}>'

    @property
    def concerns_list(self):
        """Get concerns as list"""
        if not self.concerns:
            return []
        return json.loads(self.concerns)

    @concerns_list.setter
    def concerns_list(self, value):
        """Set concerns from list"""
        self.concerns = json.dumps(value or [])

    @property
    def preferred_ingredients_list(self):
        """Get preferred ingredients as list"""
        if not self.preferred_ingredients:
            return []
        return json.loads(self.preferred_ingredients)

    @preferred_ingredients_list.setter
    def preferred_ingredients_list(self, value):
        """Set preferred ingredients from list"""
        self.preferred_ingredients = json.dumps(value or [])

    @property
    def avoided_ingredients_list(self):
        """Get avoided ingredients as list"""
        if not self.avoided_ingredients:
            return []
        return json.loads(self.avoided_ingredients)

    @avoided_ingredients_list.setter
    def avoided_ingredients_list(self, value):
        """Set avoided ingredients from list"""
        self.avoided_ingredients = json.dumps(value or [])

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skin_type': self.skin_type,
            'concerns': self.concerns_list,
            'budget_min': self.budget_min,
            'budget_max': self.budget_max,
            'preferred_ingredients': self.preferred_ingredients_list,
            'avoided_ingredients': self.avoided_ingredients_list,
            'updated_at': self.updated_at.isoformat()
        }