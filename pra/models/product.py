from pra.models.db import db
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
    routine_products = db.relationship('RoutineProduct', back_populates='product')
    shopping_list_items = db.relationship('ShoppingListItem', back_populates='product')
    product_comments = db.relationship('ProductComment', back_populates='product', cascade='all, delete-orphan')

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


class Wardrobe(db.Model):
    """User's collection of products they own or want to try"""
    __tablename__ = 'wardrobe'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)

    # Product info (stored directly if not in products table)
    product_name = db.Column(db.String(500), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=True)
    url = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)

    # Wardrobe-specific fields
    status = db.Column(db.String(50), default='want_to_try')  # 'own', 'want_to_try', 'used_to_own'
    category = db.Column(db.String(100), nullable=True)  # cleanser, serum, moisturizer, etc.
    notes = db.Column(db.Text, nullable=True)  # User's personal notes
    purchase_date = db.Column(db.DateTime, nullable=True)

    # Ratings
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref='wardrobe_items')
    product = db.relationship('Product', backref='in_wardrobes')

    def __repr__(self):
        return f'<Wardrobe {self.user_id} - {self.product_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'brand': self.brand,
            'price': self.price,
            'url': self.url,
            'image_url': self.image_url,
            'status': self.status,
            'category': self.category,
            'notes': self.notes,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'user_rating': self.user_rating,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
