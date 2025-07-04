import json
import logging
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, api_key=None):
        """Initialize EmailSender with SendGrid API key"""
        self.api_key = api_key
        if self.api_key:
            self.sg = SendGridAPIClient(api_key=self.api_key)
        else:
            self.sg = None
    
    def send_email(self, to_email, subject, html_content, from_email="noreply@leadgenius.com", from_name="LeadGenius"):
        """
        Send an email using SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            from_email: Sender email (defaults to noreply@leadgenius.com)
            from_name: Sender name (defaults to LeadGenius)
        
        Returns:
            dict: Result with success status and message
        """
        if not self.sg:
            return {
                "success": False,
                "message": "SendGrid API key not configured"
            }
        
        try:
            message = Mail(
                from_email=(from_email, from_name),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.sg.send(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return {
                "success": True,
                "message": f"Email sent successfully to {to_email}",
                "status_code": response.status_code
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}"
            }
    
    def log_email_activity(self, lead_id, to_email, subject, status, message=""):
        """
        Log email activity to a file for tracking
        
        Args:
            lead_id: ID of the lead
            to_email: Recipient email
            subject: Email subject
            status: success/failed
            message: Additional message or error details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "lead_id": lead_id,
            "to_email": to_email,
            "subject": subject,
            "status": status,
            "message": message
        }
        
        try:
            # Load existing log or create new one
            try:
                with open("email_log.json", "r") as f:
                    email_log = json.load(f)
            except FileNotFoundError:
                email_log = []
            
            # Add new entry
            email_log.append(log_entry)
            
            # Save updated log
            with open("email_log.json", "w") as f:
                json.dump(email_log, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log email activity: {str(e)}")

def format_email_content(lead_data, email_message):
    """
    Format the email content with proper HTML styling
    
    Args:
        lead_data: Lead information
        email_message: The AI-generated email message
    
    Returns:
        str: Formatted HTML email content
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Business Opportunity</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .content {{
                margin-bottom: 20px;
            }}
            .footer {{
                font-size: 12px;
                color: #666;
                border-top: 1px solid #eee;
                padding-top: 10px;
                margin-top: 20px;
            }}
            .signature {{
                margin-top: 20px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Business Growth Opportunity</h2>
        </div>
        
        <div class="content">
            {email_message.replace(chr(10), '<br>')}
        </div>
        
        <div class="signature">
            Best regards,<br>
            LeadGenius Team
        </div>
        
        <div class="footer">
            <p>This email was sent from LeadGenius lead generation system.</p>
            <p>If you don't wish to receive further communications, please reply with "UNSUBSCRIBE".</p>
        </div>
    </body>
    </html>
    """
    
    return html_content 