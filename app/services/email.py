import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        # Base directory for email templates
        self.templates_dir = Path(__file__).resolve().parent.parent / "templates" / "email"

    def _render_template(self, template_name: str, context: Dict[str, str]) -> str:
        """Render a template by simple placeholder replacement using {{key}} markers.
        This avoids adding a templating engine dependency.
        """
        template_path = self.templates_dir / template_name
        try:
            html = template_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read email template '{template_name}': {e}")
            raise
        # Simple replacement for {{key}}
        for key, value in context.items():
            html = html.replace(f"{{{{{key}}}}}", str(value))
        return html

    def send_email(self, to_emails: List[str], subject: str, body: str, is_html: bool = True) -> bool:
        """Send email to specified recipients."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject

            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to: {', '.join(to_emails)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_welcome_email(self, user_email: str, user_name: str = None) -> bool:
        """Send welcome email to new user using template."""
        subject = "Welcome to PixelForge Studio!"
        display_name = user_name or user_email.split('@')[0].title()
        body = self._render_template(
            "welcome.html",
            {"user_name": display_name}
        )
        return self.send_email([user_email], subject, body)

    def send_inquiry_notification(self, inquiry_data: dict, admin_email: str = None) -> bool:
        """Send inquiry notification to admin and confirmation to customer."""
        try:
            # Send notification to admin
            admin_recipient = admin_email or settings.admin_email
            admin_subject = f"New Inquiry: {inquiry_data['subject']}"
            
            admin_body = self._render_template(
                "inquiry_admin.html",
                {
                    "subject": inquiry_data['subject'],
                    "received_at": datetime.now().strftime('%Y-%m-%d at %H:%M'),
                    "first_name": inquiry_data['first_name'],
                    "last_name": inquiry_data['last_name'],
                    "email": inquiry_data['email'],
                    "phone_number": inquiry_data.get('phone_number', 'Not provided'),
                    "newsletter": 'Yes' if inquiry_data.get('subscribe_newsletter', False) else 'No',
                    "message": inquiry_data['message'],
                }
            )
            
            admin_success = self.send_email([admin_recipient], admin_subject, admin_body)
            
            # Send confirmation to customer
            customer_subject = f"Thank you for contacting PixelForge Studio - {inquiry_data['subject']}"
            
            customer_body = self._render_template(
                "inquiry_customer.html",
                {
                    "first_name": inquiry_data['first_name'],
                    "subject": inquiry_data['subject'],
                    "submitted_at": datetime.now().strftime('%Y-%m-%d at %H:%M'),
                    "reference": f"INQ-{datetime.now().strftime('%Y%m%d')}-{hash(inquiry_data['email']) % 10000:04d}",
                    "from_email": settings.smtp_from_email,
                }
            )
            
            customer_success = self.send_email([inquiry_data['email']], customer_subject, customer_body)
            
            logger.info(f"Inquiry emails sent - Admin: {admin_success}, Customer: {customer_success}")
            return admin_success and customer_success
            
        except Exception as e:
            logger.error(f"Failed to send inquiry emails: {str(e)}")
            return False

email_service = EmailService()
