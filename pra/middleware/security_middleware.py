"""
Advanced Security Middleware
Enterprise-grade threat detection and prevention
"""
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
from user_agents import parse
from flask import request, jsonify
from flask_login import current_user

from pra.models.db import db
from pra.models.analytics import VisitorLog, SecurityEvent

# In-memory rate limiting (use Redis in production)
rate_limit_store = defaultdict(list)
blocked_ips = set()

# Threat detection patterns
THREAT_PATTERNS = {
    'sql_injection': {
        'patterns': [
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bOR\b.*=.*)",
            r"(\bDROP\b.*\bTABLE\b)",
            r"(\bINSERT\b.*\bINTO\b)",
            r"(\bDELETE\b.*\bFROM\b)",
            r"(;.*--)",
            r"(\bEXEC\b.*\()",
            r"(xp_cmdshell)",
        ],
        'severity': 'critical'
    },
    'xss_attack': {
        'patterns': [
            r"<script[^>]*>.*</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
            r"<iframe",
            r"eval\s*\(",
        ],
        'severity': 'high'
    },
    'path_traversal': {
        'patterns': [
            r"\.\./",
            r"\.\.\\",
            r"/etc/passwd",
            r"/etc/shadow",
            r"c:\\windows",
            r"/proc/",
        ],
        'severity': 'high'
    },
    'command_injection': {
        'patterns': [
            r";\s*(ls|cat|wget|curl|nc|bash|sh)\s",
            r"\|\s*(ls|cat|wget|curl|nc|bash|sh)\s",
            r"`.*`",
            r"\$\(.*\)",
        ],
        'severity': 'critical'
    },
    'suspicious_user_agent': {
        'patterns': [
            r"(sqlmap|nikto|nmap|masscan|nessus)",
            r"(metasploit|burp|zap)",
        ],
        'severity': 'high'
    }
}


class SecurityMiddleware:
    """Advanced security monitoring and threat detection"""

    def __init__(self, app):
        self.app = app
        self._register_hooks()

    def _register_hooks(self):
        @self.app.before_request
        def security_check():
            """Check all requests for security threats"""
            ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

            # Check if IP is blocked
            if ip_address in blocked_ips:
                self._log_security_event(
                    'blocked_ip_attempt',
                    'critical',
                    f'Blocked IP {ip_address} attempted access',
                    ip_address
                )
                return jsonify({
                    'error': 'Access Denied',
                    'message': 'Your IP has been blocked due to suspicious activity'
                }), 403

            # Rate limiting check
            if not self._check_rate_limit(ip_address):
                self._log_security_event(
                    'rate_limit_exceeded',
                    'warning',
                    f'Rate limit exceeded for IP {ip_address}',
                    ip_address
                )
                return jsonify({
                    'error': 'Too Many Requests',
                    'message': 'Please slow down your requests'
                }), 429

            # Analyze request for threats
            threat_detected = self._detect_threats(request, ip_address)

            if threat_detected:
                # Auto-block IP after multiple critical threats
                self._handle_threat(ip_address, threat_detected)

        @self.app.after_request
        def track_response(response):
            """Track response metrics and security events"""
            if request.path.startswith('/static') or request.path.startswith('/analytics/api'):
                return response

            try:
                user_agent_str = request.headers.get('User-Agent', '')
                user_agent = parse(user_agent_str)
                ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

                # Track visitor
                log = VisitorLog(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    ip_address=ip_address,
                    user_agent=user_agent_str,
                    browser=user_agent.browser.family,
                    os=user_agent.os.family,
                    device=user_agent.device.family,
                    is_mobile=user_agent.is_mobile,
                    path=request.path,
                    method=request.method,
                    referrer=request.referrer
                )
                db.session.add(log)

                # Log HTTP errors as security events
                if response.status_code >= 400:
                    severity = 'error' if response.status_code >= 500 else 'warning'
                    if response.status_code == 403:
                        severity = 'high'  # Unauthorized access attempts

                    event = SecurityEvent(
                        event_type='http_error',
                        severity=severity,
                        description=f'{response.status_code} {request.method} {request.path}',
                        ip_address=ip_address,
                        user_id=current_user.id if current_user.is_authenticated else None,
                        path=request.path
                    )
                    db.session.add(event)

                db.session.commit()

            except Exception:
                db.session.rollback()

            return response

    def _check_rate_limit(self, ip_address, limit=100, window=60):
        """
        Check if IP has exceeded rate limit
        limit: max requests per window
        window: time window in seconds
        """
        now = time.time()

        # Clean old entries
        rate_limit_store[ip_address] = [
            timestamp for timestamp in rate_limit_store[ip_address]
            if now - timestamp < window
        ]

        # Add current request
        rate_limit_store[ip_address].append(now)

        # Check limit
        return len(rate_limit_store[ip_address]) <= limit

    def _detect_threats(self, request, ip_address):
        """Analyze request for security threats"""
        threats_found = []

        # Get all request data
        request_data = {
            'path': request.path,
            'args': str(request.args),
            'form': str(request.form),
            'data': request.get_data(as_text=True),
            'headers': str(request.headers),
            'user_agent': request.headers.get('User-Agent', ''),
        }

        # Check each threat category
        for threat_type, config in THREAT_PATTERNS.items():
            for pattern in config['patterns']:
                # Check all request components
                for component, data in request_data.items():
                    if re.search(pattern, data, re.IGNORECASE):
                        threats_found.append({
                            'type': threat_type,
                            'severity': config['severity'],
                            'pattern': pattern,
                            'component': component,
                            'matched_data': data[:200]  # First 200 chars
                        })

        # Log all detected threats
        for threat in threats_found:
            self._log_security_event(
                threat['type'],
                threat['severity'],
                f"{threat['type'].replace('_', ' ').title()} detected in {threat['component']}",
                ip_address,
                details=threat['matched_data']
            )

        return threats_found

    def _handle_threat(self, ip_address, threats):
        """Handle detected threats - block IP if necessary"""
        # Count critical/high severity threats from this IP
        critical_count = sum(
            1 for t in threats
            if t['severity'] in ['critical', 'high']
        )

        # Auto-block after 3 critical threats
        if critical_count >= 3:
            blocked_ips.add(ip_address)
            self._log_security_event(
                'ip_auto_blocked',
                'critical',
                f'IP {ip_address} automatically blocked after {critical_count} critical threats',
                ip_address
            )

    def _log_security_event(self, event_type, severity, description, ip_address, details=None):
        """Log security event to database and send email alerts"""
        try:
            event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                description=description,
                ip_address=ip_address,
                user_id=current_user.id if current_user.is_authenticated else None,
                path=request.path if request else None
            )
            db.session.add(event)
            db.session.commit()

            # Send email notification for critical/high severity
            if severity in ['critical', 'high']:
                try:
                    from pra.services.notification_service import get_notification_service
                    notifier = get_notification_service()
                    notifier.send_security_alert(
                        threat_type=event_type,
                        ip_address=ip_address,
                        severity=severity,
                        description=description
                    )
                except Exception:
                    # Don't fail request if notification fails
                    pass

        except Exception:
            db.session.rollback()


# Utility functions for manual IP management
def block_ip_address(ip):
    """Manually block an IP address"""
    blocked_ips.add(ip)
    try:
        event = SecurityEvent(
            event_type='ip_manual_block',
            severity='high',
            description=f'IP {ip} manually blocked by administrator',
            ip_address=ip
        )
        db.session.add(event)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def unblock_ip_address(ip):
    """Manually unblock an IP address"""
    if ip in blocked_ips:
        blocked_ips.remove(ip)
        return True
    return False


def get_blocked_ips():
    """Get list of currently blocked IPs"""
    return list(blocked_ips)
