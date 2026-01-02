#!/usr/bin/env python3
"""
Test script to demonstrate database creation and user storage
"""
import os
import sys

# Add pra directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pra'))

from app import create_app
from models.db import db
from models.user import User

def main():
    print("=" * 60)
    print("DATABASE DEMONSTRATION")
    print("=" * 60)

    # Create app
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database created!")

        # Check if database file exists
        db_path = os.path.join(os.path.dirname(__file__), 'pra', 'prra.db')
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✓ Database file exists at: {db_path}")
            print(f"  Size: {size:,} bytes")

        # Create a test user
        print("\n" + "-" * 60)
        print("Creating a test user...")

        # Check if user already exists
        existing_user = User.query.filter_by(email='demo@example.com').first()
        if existing_user:
            print(f"✓ User already exists: {existing_user.name} ({existing_user.email})")
            test_user = existing_user
        else:
            test_user = User(email='demo@example.com', name='Demo User')
            test_user.set_password('password123')

            db.session.add(test_user)
            db.session.commit()
            print("✓ User created and saved to database!")

        # Retrieve the user from database
        print("\n" + "-" * 60)
        print("Retrieving user from database...")

        retrieved_user = User.query.filter_by(email='demo@example.com').first()
        if retrieved_user:
            print(f"✓ User found in database!")
            print(f"  ID: {retrieved_user.id}")
            print(f"  Name: {retrieved_user.name}")
            print(f"  Email: {retrieved_user.email}")
            print(f"  Created: {retrieved_user.created_at}")
            print(f"  Active: {retrieved_user.is_active}")

        # Show all users
        print("\n" + "-" * 60)
        print("All users in database:")
        all_users = User.query.all()
        print(f"Total users: {len(all_users)}")
        for user in all_users:
            print(f"  - {user.name} ({user.email})")

        print("\n" + "=" * 60)
        print("DATABASE DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print(f"\nYour data is permanently stored in: {db_path}")
        print("This data will persist even after you close the app!")
        print("\nTo view the database:")
        print(f"  sqlite3 {db_path}")
        print("  > SELECT * FROM users;")

if __name__ == '__main__':
    main()
