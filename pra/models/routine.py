from datetime import datetime
import json

from pra.models.db import db


class SavedRoutine(db.Model):
    """Stores user's personalized routines with quiz parameters and GPT-generated results"""
    __tablename__ = 'saved_routines'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)  # For guest users

    # Quiz parameters
    skin_type = db.Column(db.String(50), nullable=False)
    concerns = db.Column(db.Text, nullable=True)  # JSON array
    budget = db.Column(db.String(50), nullable=False)
    lifestyle = db.Column(db.Text, nullable=True)  # JSON array
    preferred_ingredients = db.Column(db.Text, nullable=True)  # JSON array
    avoided_ingredients = db.Column(db.Text, nullable=True)  # JSON array

    # Generated routine data
    routine_data = db.Column(db.Text, nullable=False)  # JSON with AM/PM steps

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # User can have multiple routines

    # Relationships
    user = db.relationship('User', back_populates='saved_routines')

    def __repr__(self):
        return f'<SavedRoutine id={self.id} user_id={self.user_id} skin_type={self.skin_type}>'

    def get_concerns_list(self):
        """Parse concerns JSON string to list"""
        if not self.concerns:
            return []
        try:
            return json.loads(self.concerns)
        except:
            return []

    def get_lifestyle_list(self):
        """Parse lifestyle JSON string to list"""
        if not self.lifestyle:
            return []
        try:
            return json.loads(self.lifestyle)
        except:
            return []

    def get_preferred_ingredients_list(self):
        """Parse preferred ingredients JSON string to list"""
        if not self.preferred_ingredients:
            return []
        try:
            return json.loads(self.preferred_ingredients)
        except:
            return []

    def get_avoided_ingredients_list(self):
        """Parse avoided ingredients JSON string to list"""
        if not self.avoided_ingredients:
            return []
        try:
            return json.loads(self.avoided_ingredients)
        except:
            return []

    def get_routine_data(self):
        """Parse routine data JSON string to dict"""
        try:
            return json.loads(self.routine_data)
        except:
            return {}

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skin_type': self.skin_type,
            'concerns': self.get_concerns_list(),
            'budget': self.budget,
            'lifestyle': self.get_lifestyle_list(),
            'preferred_ingredients': self.get_preferred_ingredients_list(),
            'avoided_ingredients': self.get_avoided_ingredients_list(),
            'routine': self.get_routine_data(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }


class Routine(db.Model):
    __tablename__ = 'routines'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_saved = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='routines')
    routine_products = db.relationship(
        'RoutineProduct',
        back_populates='routine',
        cascade='all, delete-orphan'
    )
    shopping_lists = db.relationship('ShoppingList', back_populates='routine')

    def __repr__(self):
        return f'<Routine id={self.id} name={self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'is_saved': self.is_saved,
            'routine_products': [item.to_dict() for item in self.routine_products]
        }


class RoutineProduct(db.Model):
    __tablename__ = 'routine_products'

    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routines.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    time_of_day = db.Column(db.String(2), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50), nullable=False)

    # Relationships
    routine = db.relationship('Routine', back_populates='routine_products')
    product = db.relationship('Product', back_populates='routine_products')

    def __repr__(self):
        return (
            f'<RoutineProduct routine={self.routine_id} '
            f'product={self.product_id} time_of_day={self.time_of_day}>'
        )

    def to_dict(self):
        return {
            'id': self.id,
            'routine_id': self.routine_id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None,
            'time_of_day': self.time_of_day,
            'order': self.order,
            'category': self.category
        }


class ShoppingList(db.Model):
    __tablename__ = 'shopping_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    routine_id = db.Column(db.Integer, db.ForeignKey('routines.id'), nullable=True, index=True)
    name = db.Column(db.String(255), nullable=False, default='My Shopping List')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='shopping_lists')
    routine = db.relationship('Routine', back_populates='shopping_lists')
    shopping_list_items = db.relationship(
        'ShoppingListItem',
        back_populates='shopping_list',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<ShoppingList id={self.id} user_id={self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'routine_id': self.routine_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'shopping_list_items': [item.to_dict() for item in self.shopping_list_items],
            'total_price': sum(item.product.price or 0 for item in self.shopping_list_items if item.product)
        }


class ShoppingListItem(db.Model):
    __tablename__ = 'shopping_list_items'

    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    is_affordable_option = db.Column(db.Boolean, default=True, nullable=False)
    is_purchased = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    shopping_list = db.relationship('ShoppingList', back_populates='shopping_list_items')
    product = db.relationship('Product', back_populates='shopping_list_items')

    def __repr__(self):
        return f'<ShoppingListItem list={self.shopping_list_id} product={self.product_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'shopping_list_id': self.shopping_list_id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None,
            'is_affordable_option': self.is_affordable_option,
            'is_purchased': self.is_purchased
        }
