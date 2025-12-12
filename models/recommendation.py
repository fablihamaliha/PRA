from models.db import db
from datetime import datetime


class RecommendationSession(db.Model):
    __tablename__ = 'recommendation_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skin_profile_id = db.Column(db.Integer, db.ForeignKey('skin_profiles.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='recommendation_sessions')
    skin_profile = db.relationship('SkinProfile', back_populates='recommendation_sessions')
    items = db.relationship('RecommendationItem', back_populates='session', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<RecommendationSession id={self.id} user_id={self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skin_profile_id': self.skin_profile_id,
            'created_at': self.created_at.isoformat(),
            'items': [item.to_dict() for item in self.items]
        }


class RecommendationItem(db.Model):
    __tablename__ = 'recommendation_items'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('recommendation_sessions.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)

    rank = db.Column(db.Integer, nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text, nullable=True)

    # Relationships
    session = db.relationship('RecommendationSession', back_populates='items')
    product = db.relationship('Product', back_populates='recommendation_items')

    def __repr__(self):
        return f'<RecommendationItem session={self.session_id} rank={self.rank}>'

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None,
            'rank': self.rank,
            'match_score': round(self.match_score, 2),
            'reason': self.reason
        }