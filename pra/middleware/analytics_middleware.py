import ipaddress
import os

import requests
from user_agents import parse
from flask import request
from flask_login import current_user

from pra.models.db import db
from pra.models.analytics import VisitorLog, SecurityEvent


class AnalyticsMiddleware:
    def __init__(self, app):
        self.app = app
        self.geoip_cache = {}
        self.geoip_enabled = os.getenv('ANALYTICS_GEOIP_ENABLED', 'true').lower() == 'true'
        self._register_hooks()

    def _get_geoip(self, ip_address):
        if not self.geoip_enabled or not ip_address:
            return {}

        try:
            ip = ipaddress.ip_address(ip_address.split(',')[0].strip())
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                return {}
        except ValueError:
            return {}

        if ip_address in self.geoip_cache:
            return self.geoip_cache[ip_address]

        try:
            response = requests.get(f'https://ipapi.co/{ip_address}/json/', timeout=3)
            if response.status_code != 200:
                return {}
            data = response.json()
            location = {
                'city': data.get('city'),
                'region': data.get('region'),
                'country': data.get('country_name')
            }
            self.geoip_cache[ip_address] = location
            return location
        except Exception:
            return {}

    def _register_hooks(self):
        @self.app.before_request
        def track_visit():
            if request.path.startswith('/static') or request.path.startswith('/analytics/api'):
                return

            try:
                user_agent_str = request.headers.get('User-Agent', '')
                user_agent = parse(user_agent_str)
                ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
                geo = self._get_geoip(ip_address)

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
                    referrer=request.referrer,
                    city=geo.get('city'),
                    region=geo.get('region'),
                    country=geo.get('country')
                )
                db.session.add(log)
                db.session.commit()
            except Exception:
                db.session.rollback()

        @self.app.after_request
        def track_security(response):
            if response.status_code >= 400 and not request.path.startswith('/analytics/api'):
                try:
                    event = SecurityEvent(
                        event_type='http_error',
                        severity='warning' if response.status_code < 500 else 'error',
                        description=f'{response.status_code} on {request.path}',
                        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr),
                        user_id=current_user.id if current_user.is_authenticated else None,
                        path=request.path
                    )
                    db.session.add(event)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
            if response.status_code == 429:
                try:
                    event = SecurityEvent(
                        event_type='rate_limited',
                        severity='warning',
                        description=f'Rate limited on {request.path}',
                        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr),
                        user_id=current_user.id if current_user.is_authenticated else None,
                        path=request.path
                    )
                    db.session.add(event)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
            return response
