"""
Admin Authentication Routes
Secure authentication system for analytics dashboard access
"""
import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from pra.models.admin_user import AdminUser, FailedLoginAttempt
from pra.models.db import db

logger = logging.getLogger(__name__)

admin_auth_bp = Blueprint('admin_auth', __name__, url_prefix='/admin')


def get_client_ip():
    """Get client IP address from request"""
    return request.headers.get('X-Forwarded-For', request.remote_addr)


def is_ip_allowed(ip_address: str) -> bool:
    """Check if IP is in allowlist"""
    allowlist = (os.getenv('ADMIN_IP_ALLOWLIST', '') or '').strip()
    if not allowlist:
        return True  # No allowlist configured, allow all IPs
    allowed_ips = {ip.strip() for ip in allowlist.split(',') if ip.strip()}
    return ip_address in allowed_ips


def check_rate_limit(username: str, ip_address: str) -> tuple[bool, int]:
    """
    Check if user/IP has exceeded failed login attempts
    Returns: (is_allowed, remaining_attempts)
    """
    max_attempts = int(os.getenv('ADMIN_MAX_FAILED_ATTEMPTS', '5'))
    lockout_duration = int(os.getenv('ADMIN_LOCKOUT_DURATION', '900'))  # 15 minutes

    since = datetime.utcnow() - timedelta(seconds=lockout_duration)

    # Count recent failed attempts
    failed_count = FailedLoginAttempt.query.filter(
        FailedLoginAttempt.username == username,
        FailedLoginAttempt.attempted_at >= since
    ).count()

    remaining = max(0, max_attempts - failed_count)
    is_allowed = failed_count < max_attempts

    return is_allowed, remaining


def log_failed_attempt(username: str, ip_address: str):
    """Log a failed login attempt"""
    attempt = FailedLoginAttempt(
        username=username,
        ip_address=ip_address,
        user_agent=request.headers.get('User-Agent', '')[:500]
    )
    db.session.add(attempt)
    db.session.commit()
    logger.warning(f"Failed admin login attempt: {username} from {ip_address}")


def is_admin_authenticated() -> bool:
    """Check if current session is admin authenticated"""
    return session.get('admin_authenticated', False) and session.get('admin_username')


@admin_auth_bp.route('/login', methods=['GET'])
def login_page():
    """Admin login page"""
    if is_admin_authenticated():
        return redirect(url_for('analytics.dashboard'))

    return render_template('admin_login.html')


@admin_auth_bp.route('/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        passphrase = data.get('passphrase', '')

        # Validate input
        if not username or not passphrase:
            return jsonify({
                'success': False,
                'error': 'Username and passphrase are required'
            }), 400

        # Check IP allowlist
        client_ip = get_client_ip()
        if not is_ip_allowed(client_ip):
            logger.warning(f"Admin login attempt from unauthorized IP: {client_ip}")
            return jsonify({
                'success': False,
                'error': 'Access denied from your location'
            }), 403

        # Check rate limiting
        is_allowed, remaining = check_rate_limit(username, client_ip)
        if not is_allowed:
            lockout_min = int(os.getenv('ADMIN_LOCKOUT_DURATION', '900')) // 60
            return jsonify({
                'success': False,
                'error': f'Too many failed attempts. Try again in {lockout_min} minutes.'
            }), 429

        # Verify credentials
        admin = AdminUser.query.filter_by(username=username).first()

        if not admin or not admin.check_passphrase(passphrase):
            log_failed_attempt(username, client_ip)
            return jsonify({
                'success': False,
                'error': f'Invalid credentials. {remaining - 1} attempts remaining.',
                'remaining_attempts': remaining - 1
            }), 401

        if not admin.is_active:
            return jsonify({
                'success': False,
                'error': 'Admin account is deactivated'
            }), 403

        # Login successful
        session['admin_authenticated'] = True
        session['admin_username'] = admin.username
        session['admin_user_id'] = admin.id
        session.permanent = True

        admin.update_last_login()
        logger.info(f"Admin login successful: {username} from {client_ip}")

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'redirect': '/analytics/dashboard'
        }), 200

    except Exception as e:
        logger.error(f"Admin login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred during login'
        }), 500


@admin_auth_bp.route('/logout', methods=['POST'])
def logout():
    """Admin logout endpoint"""
    username = session.get('admin_username')
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    session.pop('admin_user_id', None)

    if username:
        logger.info(f"Admin logout: {username}")

    return jsonify({
        'success': True,
        'message': 'Logged out successfully',
        'redirect': '/admin/login'
    }), 200


@admin_auth_bp.route('/status', methods=['GET'])
def status():
    """Check admin authentication status"""
    return jsonify({
        'authenticated': is_admin_authenticated(),
        'username': session.get('admin_username') if is_admin_authenticated() else None
    }), 200
