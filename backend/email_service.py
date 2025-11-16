"""
Email Service for Password Reset
Simple email sender using SMTP or console logging for development
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@pookie4u.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.use_console = os.getenv("EMAIL_CONSOLE_MODE", "true").lower() == "true"
        
    def send_password_reset_email(self, recipient_email: str, reset_token: str, reset_link: str):
        """
        Send password reset email
        In production: sends actual email
        In development: logs to console
        """
        subject = "Reset Your Pookie4u Password"
        
        # Create HTML email body
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #FF6B9D 0%, #FEC5E5 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 15px 30px; background: #FF6B9D; 
                          color: white; text-decoration: none; border-radius: 5px; 
                          font-weight: bold; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .code {{ background: #fff; padding: 15px; border: 2px dashed #FF6B9D; 
                        border-radius: 5px; text-align: center; font-size: 24px; 
                        font-weight: bold; letter-spacing: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hi there,</p>
                    <p>We received a request to reset your Pookie4u account password. If you didn't make this request, you can safely ignore this email.</p>
                    
                    <p>To reset your password, use the code below or click the button:</p>
                    
                    <div class="code">{reset_token}</div>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px;">
                        <strong>Note:</strong> This code will expire in 1 hour for security reasons.
                    </p>
                    
                    <p>If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #FF6B9D;">{reset_link}</p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #666;">
                        For security reasons:
                        <ul>
                            <li>Never share this code with anyone</li>
                            <li>Pookie4u will never ask for your password via email</li>
                            <li>If you didn't request this, change your password immediately</li>
                        </ul>
                    </p>
                </div>
                <div class="footer">
                    <p>💕 Sent with love from Pookie4u</p>
                    <p>Making relationships stronger, one task at a time</p>
                    <p>&copy; {datetime.now().year} Pookie4u. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_body = f"""
        Password Reset Request
        
        Hi there,
        
        We received a request to reset your Pookie4u account password.
        
        Your reset code: {reset_token}
        
        Or click this link: {reset_link}
        
        This code will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        The Pookie4u Team
        """
        
        if self.use_console:
            # Development mode: log to console
            print("\n" + "="*60)
            print("📧 PASSWORD RESET EMAIL (CONSOLE MODE)")
            print("="*60)
            print(f"To: {recipient_email}")
            print(f"Subject: {subject}")
            print(f"\nReset Code: {reset_token}")
            print(f"Reset Link: {reset_link}")
            print(f"\nExpires: 1 hour from now")
            print("="*60 + "\n")
            return True
        else:
            # Production mode: send actual email
            try:
                message = MIMEMultipart("alternative")
                message["Subject"] = subject
                message["From"] = self.sender_email
                message["To"] = recipient_email
                
                # Attach both plain text and HTML versions
                part1 = MIMEText(text_body, "plain")
                part2 = MIMEText(html_body, "html")
                message.attach(part1)
                message.attach(part2)
                
                # Send email
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(message)
                
                print(f"✅ Password reset email sent to {recipient_email}")
                return True
                
            except Exception as e:
                print(f"❌ Failed to send email: {e}")
                return False

# Create singleton instance
email_service = EmailService()
