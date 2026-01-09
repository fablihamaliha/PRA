import json
import os
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from pra.models.analytics import VisitorLog, SecurityEvent, AnalyticsEvent
from pra.models.db import db


analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


def _get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)


def _is_ip_allowed(ip_address):
    allowlist = (os.getenv('ADMIN_IP_ALLOWLIST', '') or '').strip()
    if not allowlist:
        return True
    allowed = {ip.strip() for ip in allowlist.split(',') if ip.strip()}
    return ip_address in allowed


def _admin_required():
    if not (current_user.is_authenticated and current_user.email.endswith('@admin.com')):
        return False
    return _is_ip_allowed(_get_client_ip())


@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    if not _admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    stats = _get_stats_payload()
    return render_template('analytics_dashboard.html', stats=stats)


@analytics_bp.route('/api/visitors')
@login_required
def get_visitors():
    if not _admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    visitors = VisitorLog.query.order_by(VisitorLog.created_at.desc()).limit(200).all()
    return jsonify({
        'success': True,
        'visitors': [v.to_dict() for v in visitors]
    }), 200


@analytics_bp.route('/api/security-events')
@login_required
def get_security_events():
    if not _admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    events = SecurityEvent.query.order_by(SecurityEvent.created_at.desc()).limit(200).all()
    return jsonify({
        'success': True,
        'events': [e.to_dict() for e in events]
    }), 200


@analytics_bp.route('/api/stats')
@login_required
def get_stats():
    if not _admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    return jsonify({
        'success': True,
        'stats': _get_stats_payload()
    }), 200


@analytics_bp.route('/api/track-event', methods=['POST'])
def track_event():
    data = request.get_json() or {}
    event_type = data.get('event_type')

    if not event_type:
        return jsonify({'success': False, 'error': 'event_type is required'}), 400

    event = AnalyticsEvent(
        event_type=event_type,
        event_metadata=json.dumps(data.get('metadata', {})),
        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr),
        user_id=current_user.id if current_user.is_authenticated else None,
        path=request.path
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({'success': True}), 200


@analytics_bp.route('/api/events')
@login_required
def get_events():
    if not _admin_required():
        return jsonify({'error': 'Admin access required'}), 403

    events = AnalyticsEvent.query.order_by(AnalyticsEvent.created_at.desc()).limit(200).all()
    return jsonify({
        'success': True,
        'events': [e.to_dict() for e in events]
    }), 200


def _get_stats_payload():
    now = datetime.utcnow()
    since = now - timedelta(days=1)

    total_visits = VisitorLog.query.count()
    visits_today = VisitorLog.query.filter(VisitorLog.created_at >= since).count()
    unique_ips_today = db.session.query(VisitorLog.ip_address).filter(
        VisitorLog.created_at >= since
    ).distinct().count()

    total_security_events = SecurityEvent.query.count()
    recent_security_events = SecurityEvent.query.filter(SecurityEvent.created_at >= since).count()

    return {
        'total_visits': total_visits,
        'visits_last_24h': visits_today,
        'unique_ips_last_24h': unique_ips_today,
        'total_security_events': total_security_events,
        'security_events_last_24h': recent_security_events
    }
