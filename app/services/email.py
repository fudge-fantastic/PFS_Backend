import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.from_email = settings.smtp_from_email

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
        """Send welcome email to new user."""
        subject = "Welcome to PixelForge Studio!"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f4f4f4; padding: 10px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to PixelForge Studio!</h1>
                </div>
                <div class="content">
                    <h2>Hello {user_name or user_email}!</h2>
                    <p>Thank you for joining PixelForge Studio. Your account has been successfully created.</p>
                    <p>You can now browse our amazing collection of:</p>
                    <ul>
                        <li>Photo Magnets</li>
                        <li>Fridge Magnets</li>
                        <li>Retro Prints</li>
                    </ul>
                    <p>If you have any questions, feel free to contact our support team.</p>
                    <p>Best regards,<br>The PixelForge Studio Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 PixelForge Studio. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email([user_email], subject, body)

    def send_admin_product_notification(self, product_title: str, product_category: str, admin_email: str = None) -> bool:
        """Send notification to admin when new product is created."""
        recipient = admin_email or settings.admin_email
        subject = f"New Product Added: {product_title}"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .product-details {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #2196F3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Product Alert</h1>
                </div>
                <div class="content">
                    <h2>A new product has been added to the inventory!</h2>
                    <div class="product-details">
                        <p><strong>Product Title:</strong> {product_title}</p>
                        <p><strong>Category:</strong> {product_category}</p>
                        <p><strong>Added on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <p>Please review the product in the admin dashboard.</p>
                    <p>Best regards,<br>PixelForge System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email([recipient], subject, body)

    def send_inquiry_notification(self, inquiry_data: dict, admin_email: str = None) -> bool:
        """Send inquiry notification to admin and confirmation to customer."""
        try:
            # Send notification to admin
            admin_recipient = admin_email or settings.admin_email
            admin_subject = f"New Inquiry: {inquiry_data['subject']}"
            
            admin_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #9C27B0; color: white; padding: 15px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .inquiry-details {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #9C27B0; margin: 10px 0; }}
                    .contact-info {{ background-color: #e8f5e8; padding: 10px; border-radius: 5px; }}
                    .message-box {{ background-color: #fff3cd; padding: 15px; border: 1px solid #ffeaa7; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📧 New Customer Inquiry</h1>
                    </div>
                    <div class="content">
                        <h2>Inquiry Details</h2>
                        <div class="inquiry-details">
                            <p><strong>📋 Subject:</strong> {inquiry_data['subject']}</p>
                            <p><strong>📅 Received:</strong> {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
                        </div>
                        
                        <div class="contact-info">
                            <h3>👤 Customer Information</h3>
                            <p><strong>Name:</strong> {inquiry_data['first_name']} {inquiry_data['last_name']}</p>
                            <p><strong>Email:</strong> {inquiry_data['email']}</p>
                            <p><strong>Phone:</strong> {inquiry_data.get('phone_number', 'Not provided')}</p>
                            <p><strong>Newsletter Subscription:</strong> {'Yes' if inquiry_data.get('subscribe_newsletter', False) else 'No'}</p>
                        </div>
                        
                        <div class="message-box">
                            <h3>💬 Message</h3>
                            <p>{inquiry_data['message']}</p>
                        </div>
                        
                        <p><em>Please respond to this inquiry as soon as possible.</em></p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            admin_success = self.send_email([admin_recipient], admin_subject, admin_body)
            
            # Send confirmation to customer
            customer_subject = f"Thank you for contacting PixelForge Studio - {inquiry_data['subject']}"
            
            customer_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #9C27B0; color: white; padding: 15px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .confirmation-box {{ background-color: #e8f5e8; padding: 15px; border: 1px solid #4CAF50; border-radius: 5px; margin: 15px 0; }}
                    .footer {{ background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; }}
                    .highlight {{ color: #9C27B0; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✨ Thank You for Your Inquiry!</h1>
                    </div>
                    <div class="content">
                        <h2>Hello {inquiry_data['first_name']}! 👋</h2>
                        
                        <p>Thank you for reaching out to <span class="highlight">PixelForge Studio</span>. We have received your inquiry and our team will get back to you as soon as possible.</p>
                        
                        <div class="confirmation-box">
                            <h3>📋 Your Inquiry Summary</h3>
                            <p><strong>Subject:</strong> {inquiry_data['subject']}</p>
                            <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
                            <p><strong>Reference:</strong> INQ-{datetime.now().strftime('%Y%m%d')}-{hash(inquiry_data['email']) % 10000:04d}</p>
                        </div>
                        
                        <h3>🎨 What We Offer</h3>
                        <p>While you wait, feel free to explore our amazing collection:</p>
                        <ul>
                            <li>📸 <strong>Photo Magnets</strong> - Turn your memories into beautiful magnets</li>
                            <li>🧲 <strong>Fridge Magnets</strong> - Stylish and functional home decor</li>
                            <li>🖼️ <strong>Retro Prints</strong> - Vintage-style prints for your space</li>
                        </ul>
                        
                        <p>We typically respond within <span class="highlight">24 hours</span> during business days. For urgent matters, please call us directly.</p>
                        
                        <p>Best regards,<br>
                        <strong>The PixelForge Studio Team</strong><br>
                        📧 {settings.smtp_from_email}</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2025 PixelForge Studio. All rights reserved.</p>
                        <p>Creating beautiful memories, one pixel at a time.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            customer_success = self.send_email([inquiry_data['email']], customer_subject, customer_body)
            
            logger.info(f"Inquiry emails sent - Admin: {admin_success}, Customer: {customer_success}")
            return admin_success and customer_success
            
        except Exception as e:
            logger.error(f"Failed to send inquiry emails: {str(e)}")
            return False

email_service = EmailService()
