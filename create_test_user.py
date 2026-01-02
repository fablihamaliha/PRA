#!/usr/bin/env python3
"""Create a test user to demonstrate data persistence"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pra'))

from app import create_app
from models.db import db
from models.user import User

app = create_app()

with app.app_context():
    # Create a new user
    test_user = User(email='test@example.com', name='Test User')
    test_user.set_password('password123')

    # Check if user already exists
    existing = User.query.filter_by(email='test@example.com').first()
    if existing:
        print(f"User already exists: {existing.name}")
    else:
        db.session.add(test_user)
        db.session.commit()
        print(f"✓ Created user: {test_user.name} ({test_user.email})")

    # Show all users
    print("\nAll users in database:")
    for user in User.query.all():
        print(f"  - ID {user.id}: {user.name} ({user.email})")
