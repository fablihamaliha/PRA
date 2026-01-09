from user_agents import parse
from flask import request
from flask_login import current_user

from pra.models.db import db
from pra.models.analytics import VisitorLog, SecurityEvent


class AnalyticsMiddleware:
    def __init__(self, app):
        self.app = app
        self._register_hooks()

    def _register_hooks(self):
        @self.app.before_request
        def track_visit():
            if request.path.startswith('/static') or request.path.startswith('/analytics/api'):
                return

            try:
                user_agent_str = request.headers.get('User-Agent', '')
                user_agent = parse(user_agent_str)
                ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

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
            return response
