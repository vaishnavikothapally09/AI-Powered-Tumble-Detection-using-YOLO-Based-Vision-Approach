import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime

class EmailService:
    def __init__(self):
        """Initialize email service with SMTP configuration"""
        # SMTP Configuration
        # Default values (can be overridden via environment variables)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '227z1a0587@gmail.com')
        self.smtp_password = os.getenv('SMTP_PASSWORD', 'fuje rdmi uted ygmv')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        
        # Verify configuration
        if self.smtp_username and self.smtp_password:
            print(f"Email service configured for: {self.smtp_username}")
        else:
            print("Warning: SMTP credentials not configured. Email functionality will be disabled.")
    
    def send_tumble_alert(self, recipient_email, image_path, status="Tumble Detected"):
        """
        Send email alert with tumble detection image
        
        Args:
            recipient_email: Email address to send alert to
            image_path: Path to the image file
            status: Status message about the tumble
        """
        if not self.smtp_username or not self.smtp_password:
            print("Email service not configured. Skipping email send.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = recipient_email
            msg['Subject'] = f"🚨 Tumble Detection Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Email body
            body = f"""
            <html>
                <body>
                    <h2>Tumble Detection Alert</h2>
                    <p><strong>Status:</strong> {status}</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>A tumble has been detected in the monitoring area. Please check on the person immediately.</p>
                    <p>Please find the captured image attached below.</p>
                    <br>
                    <p>Stay safe!</p>
                    <p>Tumble Detection System</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Attach image
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    img_data = f.read()
                    image = MIMEImage(img_data, name=os.path.basename(image_path))
                    msg.attach(image)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"Tumble alert email sent successfully to {recipient_email}")
            
            # Clean up temporary image file
            if os.path.exists(image_path) and 'temp_' in image_path:
                try:
                    os.remove(image_path)
                except:
                    pass
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("SMTP Authentication Error: Check your email credentials")
            return False
        except smtplib.SMTPException as e:
            print(f"SMTP Error: {e}")
            return False
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_test_email(self, recipient_email):
        """
        Send a test email to verify SMTP configuration
        
        Args:
            recipient_email: Email address to send test email to
        """
        if not self.smtp_username or not self.smtp_password:
            print("Email service not configured.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = recipient_email
            msg['Subject'] = "Tumble Detection System - Test Email"
            
            body = """
            <html>
                <body>
                    <h2>Test Email from Tumble Detection System</h2>
                    <p>This is a test email to verify that the email service is configured correctly.</p>
                    <p>If you receive this email, your SMTP configuration is working properly.</p>
                    <br>
                    <p>Tumble Detection System</p>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"Test email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"Error sending test email: {e}")
            return False

