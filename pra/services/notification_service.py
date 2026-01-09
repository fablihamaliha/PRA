"""
Email Notification Service
Sends alerts for critical app issues (Dynatrace-style monitoring)
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class NotificationService:
    """Send email notifications for critical app issues"""

    def __init__(self):
        self.enabled = os.getenv('EMAIL_NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)

        if self.enabled and not all([self.smtp_username, self.smtp_password]):
            logger.warning("Email notifications enabled but credentials not configured")
            self.enabled = False

    def send_critical_alert(self, subject, message, details=None):
        """Send critical security/error alert"""
        if not self.enabled:
            logger.info(f"Email notification (disabled): {subject}")
            return False

        try:
            html_content = self._build_alert_email(subject, message, details, 'critical')
            return self._send_email(subject, html_content)
        except Exception as e:
            logger.error(f"Failed to send critical alert: {str(e)}")
            return False

    def send_warning_alert(self, subject, message, details=None):
        """Send warning alert"""
        if not self.enabled:
            logger.info(f"Email notification (disabled): {subject}")
            return False

        try:
            html_content = self._build_alert_email(subject, message, details, 'warning')
            return self._send_email(subject, html_content)
        except Exception as e:
            logger.error(f"Failed to send warning alert: {str(e)}")
            return False

    def send_security_alert(self, threat_type, ip_address, severity, description):
        """Send security threat alert"""
        subject = f"🚨 Security Alert: {threat_type} - {severity.upper()}"
        message = f"Security threat detected from IP: {ip_address}"
        details = {
            'Threat Type': threat_type,
            'Severity': severity.upper(),
            'IP Address': ip_address,
            'Description': description,
            'Time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        }

        return self.send_critical_alert(subject, message, details)

    def send_performance_alert(self, metric, value, threshold):
        """Send performance degradation alert"""
        subject = f"⚠️ Performance Alert: {metric}"
        message = f"{metric} has exceeded threshold"
        details = {
            'Metric': metric,
            'Current Value': value,
            'Threshold': threshold,
            'Time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        }

        return self.send_warning_alert(subject, message, details)

    def send_error_alert(self, error_type, error_message, traceback=None):
        """Send application error alert"""
        subject = f"❌ Application Error: {error_type}"
        message = error_message
        details = {
            'Error Type': error_type,
            'Message': error_message,
            'Time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        }
        if traceback:
            details['Traceback'] = traceback

        return self.send_critical_alert(subject, message, details)

    def _build_alert_email(self, subject, message, details, severity):
        """Build HTML email content"""
        severity_colors = {
            'critical': '#ff4757',
            'warning': '#ffa502',
            'info': '#5b8def'
        }

        color = severity_colors.get(severity, '#5b8def')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 8px 8px; }}
                .details {{ background: white; padding: 15px; border-radius: 6px; margin-top: 15px; }}
                .detail-row {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
                .detail-row:last-child {{ border-bottom: none; }}
                .label {{ font-weight: 600; color: #666; }}
                .value {{ color: #333; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">{subject}</h2>
                </div>
                <div class="content">
                    <p><strong>{message}</strong></p>

                    {self._format_details(details) if details else ''}

                    <div style="margin-top: 20px;">
                        <p><strong>Action Required:</strong></p>
                        <ul>
                            <li>Review the security dashboard immediately</li>
                            <li>Check system logs for additional context</li>
                            <li>Take appropriate action if needed</li>
                        </ul>
                    </div>

                    <div style="margin-top: 20px;">
                        <a href="https://skincares.work/analytics/dashboard"
                           style="display: inline-block; background: {color}; color: white; padding: 12px 24px;
                                  text-decoration: none; border-radius: 6px;">
                            View Dashboard →
                        </a>
                    </div>
                </div>
                <div class="footer">
                    <p>This is an automated alert from your Application Monitoring System</p>
                    <p>Sent at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _format_details(self, details):
        """Format details dictionary as HTML"""
        if not details:
            return ''

        html = '<div class="details">'
        for key, value in details.items():
            html += f'''
            <div class="detail-row">
                <span class="label">{key}:</span>
                <span class="value">{value}</span>
            </div>
            '''
        html += '</div>'

        return html

    def _send_email(self, subject, html_content):
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = self.admin_email

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {self.admin_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False


# Global notification service instance
_notification_service = None


def get_notification_service():
    """Get or create notification service instance"""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service
