"""Analytics tracking utilities for visitor monitoring and geolocation"""
import requests
import re
from datetime import datetime
from flask import request, g
from user_agents import parse
from pra.models.db import db
from pra.models.analytics import VisitorLog, PageView, UserActivity, SecurityEvent
import logging

logger = logging.getLogger(__name__)


class AnalyticsTracker:
    """Main analytics tracking class"""

    @staticmethod
    def get_client_ip():
        """Get the real client IP address, accounting for proxies"""
        # Check for X-Forwarded-For header (common in proxied requests)
        if request.headers.getlist("X-Forwarded-For"):
            ip = request.headers.getlist("X-Forwarded-For")[0].split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        else:
            ip = request.remote_addr
        return ip

    @staticmethod
    def get_location_from_ip(ip_address):
        """Get geolocation data from IP address using ipapi.co (free tier)"""
        try:
            # Skip localhost
            if ip_address in ['127.0.0.1', 'localhost', '::1']:
                return {
                    'country': 'Local',
                    'country_code': 'LO',
                    'region': 'Local',
                    'city': 'Local',
                    'latitude': None,
                    'longitude': None,
                    'timezone': None,
                    'isp': 'Local'
                }

            # Call geolocation API
            response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=2)
            if response.status_code == 200:
                data = response.json()
                return {
                    'country': data.get('country_name'),
                    'country_code': data.get('country_code'),
                    'region': data.get('region'),
                    'city': data.get('city'),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'timezone': data.get('timezone'),
                    'isp': data.get('org')
                }
        except Exception as e:
            logger.warning(f"Failed to get location for IP {ip_address}: {str(e)}")

        return {
            'country': None,
            'country_code': None,
            'region': None,
            'city': None,
            'latitude': None,
            'longitude': None,
            'timezone': None,
            'isp': None
        }

    @staticmethod
    def detect_bot(user_agent_string):
        """Detect if request is from a bot"""
        if not user_agent_string:
            return True

        bot_patterns = [
            r'bot', r'crawl', r'spider', r'scrape',
            r'google', r'bing', r'yahoo', r'baidu',
            r'facebook', r'twitter', r'linkedin',
            r'curl', r'wget', r'python-requests'
        ]

        user_agent_lower = user_agent_string.lower()
        for pattern in bot_patterns:
            if re.search(pattern, user_agent_lower):
                return True

        return False

    @staticmethod
    def detect_suspicious_activity(ip_address, path, user_agent):
        """Detect potentially suspicious activity"""
        suspicious_patterns = [
            r'\.\./', r'/etc/passwd', r'/proc/', r'cmd=',
            r'<script', r'javascript:', r'eval\(', r'union.*select',
            r'drop.*table', r'insert.*into', r';.*--', r'xp_cmdshell'
        ]

        # Check path for suspicious patterns
        for pattern in suspicious_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return True, 'high', 'Suspicious pattern in URL'

        # Check for SQL injection attempts
        query_string = request.query_string.decode('utf-8', errors='ignore')
        for pattern in suspicious_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                return True, 'high', 'Potential SQL injection attempt'

        # Check for missing or suspicious user agent
        if not user_agent or len(user_agent) < 10:
            return True, 'low', 'Missing or suspicious user agent'

        return False, None, None

    @staticmethod
    def parse_user_agent(user_agent_string):
        """Parse user agent string to extract device info"""
        if not user_agent_string:
            return {'device_type': 'Unknown', 'browser': 'Unknown', 'os': 'Unknown'}

        user_agent = parse(user_agent_string)

        device_type = 'desktop'
        if user_agent.is_mobile:
            device_type = 'mobile'
        elif user_agent.is_tablet:
            device_type = 'tablet'
        elif user_agent.is_bot:
            device_type = 'bot'

        return {
            'device_type': device_type,
            'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
            'os': f"{user_agent.os.family} {user_agent.os.version_string}"
        }

    @staticmethod
    def track_visitor(user_id=None, status_code=None, response_time_ms=None):
        """Track a visitor and their request"""
        try:
            ip_address = AnalyticsTracker.get_client_ip()
            user_agent = request.headers.get('User-Agent', '')
            path = request.path
            method = request.method
            referrer = request.headers.get('Referer')
            query_string = request.query_string.decode('utf-8', errors='ignore')

            # Get location data (cached in g to avoid multiple API calls per request)
            if not hasattr(g, 'location_data'):
                g.location_data = AnalyticsTracker.get_location_from_ip(ip_address)
            location = g.location_data

            # Detect bot
            is_bot = AnalyticsTracker.detect_bot(user_agent)

            # Detect suspicious activity
            is_suspicious, threat_level, threat_desc = AnalyticsTracker.detect_suspicious_activity(
                ip_address, path, user_agent
            )

            # Create visitor log
            visitor_log = VisitorLog(
                ip_address=ip_address,
                user_agent=user_agent,
                country=location.get('country'),
                country_code=location.get('country_code'),
                region=location.get('region'),
                city=location.get('city'),
                latitude=location.get('latitude'),
                longitude=location.get('longitude'),
                timezone=location.get('timezone'),
                isp=location.get('isp'),
                path=path,
                method=method,
                referrer=referrer,
                query_string=query_string,
                session_id=request.cookies.get('session'),
                user_id=user_id,
                status_code=status_code,
                response_time_ms=response_time_ms,
                is_bot=is_bot,
                is_suspicious=is_suspicious,
                threat_level=threat_level
            )

            db.session.add(visitor_log)
            db.session.commit()

            # Log security event if suspicious
            if is_suspicious:
                AnalyticsTracker.log_security_event(
                    event_type='suspicious_request',
                    severity=threat_level,
                    description=threat_desc,
                    ip_address=ip_address,
                    user_id=user_id,
                    path=path,
                    method=method
                )

            return visitor_log

        except Exception as e:
            logger.error(f"Error tracking visitor: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def track_page_view(url, title=None, user_id=None):
        """Track a page view"""
        try:
            user_agent = request.headers.get('User-Agent', '')
            device_info = AnalyticsTracker.parse_user_agent(user_agent)

            page_view = PageView(
                url=url,
                title=title,
                path=request.path,
                session_id=request.cookies.get('session', 'unknown'),
                user_id=user_id,
                device_type=device_info.get('device_type'),
                browser=device_info.get('browser'),
                os=device_info.get('os')
            )

            db.session.add(page_view)
            db.session.commit()

            return page_view

        except Exception as e:
            logger.error(f"Error tracking page view: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def track_user_activity(user_id, activity_type, activity_category=None, description=None, metadata=None):
        """Track a specific user activity"""
        try:
            activity = UserActivity(
                user_id=user_id,
                session_id=request.cookies.get('session', 'unknown'),
                activity_type=activity_type,
                activity_category=activity_category,
                description=description,
                ip_address=AnalyticsTracker.get_client_ip(),
                path=request.path,
                metadata=metadata
            )

            db.session.add(activity)
            db.session.commit()

            return activity

        except Exception as e:
            logger.error(f"Error tracking user activity: {str(e)}")
            db.session.rollback()
            return None

    @staticmethod
    def log_security_event(event_type, severity, description, ip_address, user_id=None, path=None, method=None, payload=None, action_taken=None, is_blocked=False):
        """Log a security event"""
        try:
            security_event = SecurityEvent(
                event_type=event_type,
                severity=severity,
                description=description,
                ip_address=ip_address,
                user_id=user_id,
                user_agent=request.headers.get('User-Agent'),
                path=path,
                method=method,
                payload=payload,
                action_taken=action_taken,
                is_blocked=is_blocked
            )

            db.session.add(security_event)
            db.session.commit()

            # Log critical events
            if severity in ['high', 'critical']:
                logger.warning(f"Security Event [{severity}]: {event_type} from {ip_address} - {description}")

            return security_event

        except Exception as e:
            logger.error(f"Error logging security event: {str(e)}")
            db.session.rollback()
            return None
