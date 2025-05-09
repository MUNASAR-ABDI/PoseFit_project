import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send email via Gmail SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: Email body in HTML format
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    from_email = 'mounassar34@gmail.com'
    app_password = os.getenv('GMAIL_APP_PASSWORD')  # Get password from environment
    
    if not app_password:
        print("Error: GMAIL_APP_PASSWORD not set in environment")
        return False

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, app_password)
            server.send_message(msg)
            print("Email sent successfully")
            return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication Error: Check your email and app password")
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
    
    return False
