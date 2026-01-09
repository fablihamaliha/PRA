"""
Admin User Model for Secure Analytics Access
Separate from regular users for enhanced security
"""
from datetime import datetime
from pra.models.db import db
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import logging

logger = logging.getLogger(__name__)
ph = PasswordHasher()


class AdminUser(db.Model):
    """Admin user with secure passphrase authentication"""
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    passphrase_hash = db.Column(db.String(255), nullable=False)  # Argon2 hash
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

    def set_passphrase(self, passphrase: str):
        """Hash and set passphrase using Argon2"""
        self.passphrase_hash = ph.hash(passphrase)

    def check_passphrase(self, passphrase: str) -> bool:
        """Verify passphrase against stored hash"""
        try:
            ph.verify(self.passphrase_hash, passphrase)
            # Optionally rehash if parameters changed
            if ph.check_needs_rehash(self.passphrase_hash):
                self.set_passphrase(passphrase)
                db.session.commit()
            return True
        except VerifyMismatchError:
            return False

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class FailedLoginAttempt(db.Model):
    """Track failed admin login attempts for rate limiting"""
    __tablename__ = 'failed_login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    ip_address = db.Column(db.String(50), nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_agent = db.Column(db.String(500))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'ip_address': self.ip_address,
            'attempted_at': self.attempted_at.isoformat() if self.attempted_at else None,
            'user_agent': self.user_agent
        }
