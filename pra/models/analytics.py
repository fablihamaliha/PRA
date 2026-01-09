from datetime import datetime

from pra.models.db import db


class VisitorLog(db.Model):
    __tablename__ = 'visitor_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    ip_address = db.Column(db.String(64), nullable=True, index=True)
    user_agent = db.Column(db.Text, nullable=True)
    browser = db.Column(db.String(100), nullable=True)
    os = db.Column(db.String(100), nullable=True)
    device = db.Column(db.String(100), nullable=True)
    is_mobile = db.Column(db.Boolean, default=False, nullable=False)
    path = db.Column(db.String(500), nullable=True)
    method = db.Column(db.String(10), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='visitor_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'browser': self.browser,
            'os': self.os,
            'device': self.device,
            'is_mobile': self.is_mobile,
            'path': self.path,
            'method': self.method,
            'referrer': self.referrer,
            'city': self.city,
            'region': self.region,
            'country': self.country,
            'created_at': self.created_at.isoformat()
        }


class SecurityEvent(db.Model):
    __tablename__ = 'security_events'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(50), default='info', nullable=False)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(64), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='security_events')

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'severity': self.severity,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_id': self.user_id,
            'path': self.path,
            'created_at': self.created_at.isoformat()
        }


class AnalyticsEvent(db.Model):
    __tablename__ = 'analytics_events'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    event_metadata = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(64), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='analytics_events')

    def to_dict(self):
        return {
            'id': self.id,
            'event_type': self.event_type,
            'metadata': self.event_metadata,
            'ip_address': self.ip_address,
            'user_id': self.user_id,
            'path': self.path,
            'created_at': self.created_at.isoformat()
        }
