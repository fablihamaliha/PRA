from models.db import db
from datetime import datetime
import json


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(255), nullable=True, index=True)

    # Basic info
    name = db.Column(db.String(500), nullable=False)
    brand = db.Column(db.String(255), nullable=False, index=True)

    # Pricing
    price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default='USD')

    # Links
    url = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)

    # Source
    source = db.Column(db.String(100), nullable=False)

    # Product details (stored as JSON strings)
    skin_types = db.Column(db.Text)
    tags = db.Column(db.Text)
    ingredients = db.Column(db.Text)

    # Ratings
    rating = db.Column(db.Float, nullable=True)
    num_reviews = db.Column(db.Integer, default=0)

    # Metadata
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recommendation_items = db.relationship('RecommendationItem', back_populates='product')

    def __repr__(self):
        return f'<Product {self.brand} - {self.name}>'

    @property
    def skin_types_list(self):
        if not self.skin_types:
            return []
        return json.loads(self.skin_types)

    @skin_types_list.setter
    def skin_types_list(self, value):
        self.skin_types = json.dumps(value or [])

    @property
    def tags_list(self):
        if not self.tags:
            return []
        return json.loads(self.tags)

    @tags_list.setter
    def tags_list(self, value):
        self.tags = json.dumps(value or [])

    @property
    def ingredients_list(self):
        if not self.ingredients:
            return []
        return json.loads(self.ingredients)

    @ingredients_list.setter
    def ingredients_list(self, value):
        self.ingredients = json.dumps(value or [])

    def to_dict(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            'name': self.name,
            'brand': self.brand,
            'price': self.price,
            'currency': self.currency,
            'url': self.url,
            'image_url': self.image_url,
            'source': self.source,
            'skin_types': self.skin_types_list,
            'tags': self.tags_list,
            'ingredients': self.ingredients_list,
            'rating': self.rating,
            'num_reviews': self.num_reviews,
            'last_seen_at': self.last_seen_at.isoformat()
        }