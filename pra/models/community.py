"""
Community Models
Models for social features like product comments and reviews
"""

from datetime import datetime
from pra.models.db import db


class ProductComment(db.Model):
    """User comments on products"""
    __tablename__ = 'product_comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)

    # Comment content
    comment_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars (optional)

    # Helpful votes
    helpful_count = db.Column(db.Integer, default=0, nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_edited = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='product_comments')
    product = db.relationship('Product', back_populates='product_comments')
    helpful_votes = db.relationship('CommentHelpfulVote', back_populates='comment', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ProductComment id={self.id} user={self.user_id} product={self.product_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Anonymous',
            'product_id': self.product_id,
            'comment_text': self.comment_text,
            'rating': self.rating,
            'helpful_count': self.helpful_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_edited': self.is_edited
        }


class CommentHelpfulVote(db.Model):
    """Track which users found which comments helpful"""
    __tablename__ = 'comment_helpful_votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('product_comments.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User')
    comment = db.relationship('ProductComment', back_populates='helpful_votes')

    # Ensure each user can only vote once per comment
    __table_args__ = (
        db.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_vote'),
    )

    def __repr__(self):
        return f'<CommentHelpfulVote user={self.user_id} comment={self.comment_id}>'
