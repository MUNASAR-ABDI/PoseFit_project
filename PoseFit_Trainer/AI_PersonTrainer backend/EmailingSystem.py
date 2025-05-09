import json
import os
import smtplib
import ssl
import random
import string
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables at module level
load_dotenv()

# Constants
DEFAULT_SENDER = os.getenv('EMAIL_SENDER', 'mounassar34@gmail.com')
CREDENTIALS_FILE = 'email_credentials.json'
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))  # TLS port
SENDER_EMAIL = os.getenv('SENDER_EMAIL', "mounassar34@gmail.com")
APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', "hsxc unvk siak pltv")

def format_time(seconds):
    """Format seconds into minutes and seconds string"""
    minutes, seconds = divmod(float(seconds), 60)
    return f"{int(minutes)}m {int(seconds)}s"

def get_email_credentials():
    """Get email credentials from environment or credentials file"""
    # First try environment variable
    app_password = os.getenv('GMAIL_APP_PASSWORD')
    
    if app_password:
        print("[EmailingSystem] Using email credentials from environment variables")
        return {
            "sender_email": os.getenv('SENDER_EMAIL', DEFAULT_SENDER),
            "password": app_password,
            "smtp_server": os.getenv('SMTP_SERVER', SMTP_SERVER),
            "smtp_port": int(os.getenv('SMTP_PORT', SMTP_PORT))
        }
    
    # Fall back to credentials file
    try:
        credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CREDENTIALS_FILE)
        if os.path.exists(credentials_path):
            print(f"[EmailingSystem] Loading credentials from file: {credentials_path}")
            with open(credentials_path, 'r') as f:
                creds = json.load(f)
                if creds.get("sender_email") and creds.get("password"):
                    return creds
    except Exception as e:
        print(f"[EmailingSystem] Error loading credentials from file: {e}")
    
    # Fall back to hardcoded credentials if defined
    if SENDER_EMAIL and APP_PASSWORD:
        print("[EmailingSystem] Using hardcoded email credentials")
        return {
            "sender_email": SENDER_EMAIL,
            "password": APP_PASSWORD,
            "smtp_server": SMTP_SERVER,
            "smtp_port": SMTP_PORT
        }
    
    print("[EmailingSystem] ERROR: Email credentials not found. Emails cannot be sent.")
    print("[EmailingSystem] Please set the GMAIL_APP_PASSWORD and SENDER_EMAIL environment variables or create a credentials file.")
    return None

def send_smtp_email(recipient, message):
    """Send email using SMTP with TLS"""
    try:
        # Get credentials
        creds = get_email_credentials()
        if not creds:
            print("[EmailingSystem] ERROR: No email credentials available, cannot send email")
            return False
            
        sender_email = creds.get("sender_email", SENDER_EMAIL)
        password = creds.get("password")
        smtp_server = creds.get("smtp_server", SMTP_SERVER)
        smtp_port = creds.get("smtp_port", SMTP_PORT)
        
        if not sender_email or not password:
            print("[EmailingSystem] ERROR: Missing email or password")
            return False
        
        print(f"\n[Email System] Starting email send process to {recipient}")
        print(f"[Email System] Using sender email: {sender_email}")
        print(f"[Email System] Server: {smtp_server}:{smtp_port}")
        
        # Create server connection
        print("[Email System] Creating SMTP connection...")
        
        # Create SSL context with proper verification
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Connect to SMTP server using hostname (not IP)
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        
        try:
            # Start TLS with proper context
            print("[Email System] Starting TLS encryption...")
            server.starttls(context=context)
            
            # Login
            print(f"[Email System] Attempting login for {sender_email}...")
            server.login(sender_email, password)
            print("[Email System] Login successful!")
            
            # Send the message
            print("[Email System] Sending message...")
            message['From'] = sender_email  # Ensure From address is set correctly
            result = server.send_message(message)
            print(f"[Email System] Message sent successfully! Result: {result}")
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"\n[Email System] Authentication Error!")
            print(f"[Email System] Error details: {str(e)}")
            print(f"[Email System] Error code: {e.smtp_code}")
            print(f"[Email System] Error message: {e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else e.smtp_error}")
            print("\n[Email System] This is likely due to an invalid app password. Please update your Gmail App Password.")
            print("[Email System] Instructions: Go to your Google Account > Security > App passwords to generate a new one")
            return False
            
        except smtplib.SMTPException as e:
            print(f"\n[Email System] SMTP Error: {str(e)}")
            print(f"[Email System] Error type: {type(e)}")
            if hasattr(e, 'smtp_code'):
                print(f"[Email System] SMTP code: {e.smtp_code}")
            if hasattr(e, 'smtp_error'):
                print(f"[Email System] SMTP error: {e.smtp_error}")
            return False
            
        finally:
            try:
                print("[Email System] Closing SMTP connection...")
                server.quit()
            except Exception as e:
                print(f"[Email System] Error closing connection: {str(e)}")
                
    except Exception as e:
        print(f"\n[Email System] Unexpected error: {str(e)}")
        print(f"[Email System] Error type: {type(e)}")
        if hasattr(e, '__dict__'):
            print("[Email System] Full error details:", str(e.__dict__))
        return False

def email_user(email, name, calories, time, rep_completion=None):
    """
    Send a workout summary email to the user.
    
    Args:
        email: User's email address
        name: User's first name
        calories: Calories burned during workout
        time: Time elapsed during workout (in seconds)
        rep_completion: Optional percentage of reps completed (0-100)
    
    Returns:
        True if email was sent successfully, False otherwise
    """
    # Validate inputs
    if not email or not name:
        print("Error: Email and name are required")
        return False
    
    # Get credentials
    creds = get_email_credentials()
    if not creds:
        return False
    
    try:
        print(f"Preparing workout summary email for {name} ({email})")
        
        # Format data for display
        calories_formatted = f"{calories}" if calories else "0"
        time_formatted = format_time(time)
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create HTML content
        html_content = create_workout_summary_html(
            name, 
            today_date, 
            calories_formatted, 
            time_formatted, 
            rep_completion
        )
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = creds["sender_email"]
        msg['To'] = email
        msg['Subject'] = f"Your Workout Summary - {today_date}"
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send the email
        result = send_smtp_email(email, msg)
        
        if result:
            print("Workout summary sent successfully")
        else:
            print(f"Failed to send workout summary email to {email}")
            
        return result
        
    except Exception as e:
        print(f"Error sending workout summary email: {e}")
        return False

def create_workout_summary_html(name, date, calories, time, rep_completion=None):
    """Create HTML content for workout summary email"""
    # Greeting
    greeting = f'<p style="font-size:22px; text-align: center;">Hi {name}!</p>'
    
    # Performance summary
    performance_summary = '<p style="font-size:20px; text-align: center;"><b>Here is your Performance Summary</b> for '
    date_calories_time = f'{date}:</p><br><p style="font-size:18px; text-align: center;">CALORIES BURNED: {calories}<br><br>TOTAL WORKOUT TIME: {time}</p>'
    
    # Rep completion if provided
    rep_completion_text = ""
    if rep_completion is not None:
        rep_completion_formatted = f"{int(rep_completion)}%"
        rep_completion_text = f'<p style="font-size:18px; text-align: center;">REP COMPLETION: {rep_completion_formatted}</p>'
    
    # Motivation
    motivation = '<p style="font-size:16px; text-align: center;">Keep up the great work! Remember, consistency is key.</p>'
    
    # Combine all parts
    return greeting + performance_summary + date_calories_time + rep_completion_text + motivation

def email_with_attachment(email, name, subject, html_content, attachment_path):
    """
    Send email with an attachment
    
    Args:
        email: Recipient email address
        name: Recipient name
        subject: Email subject
        html_content: HTML email body
        attachment_path: Path to file to attach
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Validate inputs
    if not email or not name or not subject or not html_content:
        print("Error: Required email parameters missing")
        return False
    
    # Get credentials
    creds = get_email_credentials()
    if not creds:
        return False
    
    try:
        # Convert to absolute path if not already
        attachment_path = os.path.abspath(attachment_path)
        
        # Verify attachment exists
        if not os.path.exists(attachment_path):
            print(f"Attachment file not found: {attachment_path}")
            return False
            
        # Create message
        msg = MIMEMultipart()
        msg['From'] = creds["sender_email"]
        msg['To'] = email
        msg['Subject'] = subject
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Attach file
        try:
            with open(attachment_path, 'rb') as file:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(file.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition', 
                    f'attachment; filename="{os.path.basename(attachment_path)}"'
                )
                msg.attach(attachment)
        except Exception as e:
            print(f"Error attaching file: {e}")
            return False
        
        # Send email
        result = send_smtp_email(email, msg)
        
        if result:
            print(f"Email with attachment sent successfully to {email}")
            
        return result
            
    except Exception as e:
        print(f"Error sending email with attachment: {e}")
        return False

def email_user_with_video(recipient_email, recipient_name, calories, time_elapsed, video_path=None):
    """
    Send an email to the user with their workout summary and optionally a video attachment
    
    Args:
        recipient_email: User's email address
        recipient_name: User's first name
        calories: Calories burned during workout
        time_elapsed: Time elapsed during workout (in seconds)
        video_path: Optional path to video file to attach
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Validate inputs
    if not recipient_email or not recipient_name:
        print("[EmailingSystem] Error: recipient email and name are required")
        return False
        
    if video_path and not os.path.exists(video_path):
        print(f"[EmailingSystem] Error: Video file not found: {video_path}")
        return False
        
    # Validate video file
    if video_path:
        try:
            file_size = os.path.getsize(video_path)
            print(f"[EmailingSystem] Video file size: {file_size} bytes")
            
            if file_size == 0:
                print(f"[EmailingSystem] Warning: Video file exists but is empty: {video_path}")
                # Continue without attachment
                video_path = None
            elif file_size > 25 * 1024 * 1024:  # 25MB max for most email servers
                print(f"[EmailingSystem] Warning: Video file is too large for email attachment: {file_size} bytes")
                # Try to compress the video or offer an alternative
                try:
                    import subprocess
                    compressed_path = video_path.replace('.mp4', '_email_compressed.mp4')
                    if video_path.endswith('.avi'):
                        compressed_path = video_path.replace('.avi', '_email_compressed.mp4')
                        
                    # Use ffmpeg to create a more compressed version for email
                    ffmpeg_cmd = [
                        'ffmpeg',
                        '-y',
                        '-i', video_path,
                        '-vcodec', 'libx264',
                        '-crf', '30',  # Higher compression
                        '-preset', 'veryfast',
                        '-s', '640x360',  # Smaller resolution
                        '-movflags', '+faststart',
                        compressed_path
                    ]
                    
                    print(f"[EmailingSystem] Attempting to compress video for email: {' '.join(ffmpeg_cmd)}")
                    result = subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                    
                    if os.path.exists(compressed_path) and os.path.getsize(compressed_path) < 20 * 1024 * 1024:
                        print(f"[EmailingSystem] Using compressed video for email: {compressed_path} ({os.path.getsize(compressed_path)} bytes)")
                        video_path = compressed_path
                    else:
                        print("[EmailingSystem] Compression failed or file still too large, will send email without attachment")
                        # Continue without attachment
                        video_path = None
                except Exception as e:
                    print(f"[EmailingSystem] Error compressing video: {e}")
                    # Continue without attachment
                    video_path = None
        except Exception as e:
            print(f"[EmailingSystem] Error checking video file: {e}")
            # Continue without attachment
            video_path = None
    
    try:
        # Get email credentials
        email_config = get_email_credentials()
        if not email_config:
            print("[EmailingSystem] Error: No email configuration available")
            return False
            
        sender_email = email_config.get('sender_email')
        sender_password = email_config.get('password')
        smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = email_config.get('smtp_port', 587)
        
        if not sender_email or not sender_password:
            print("[EmailingSystem] Error: Missing email credentials")
            return False
            
        # Format time for email
        time_formatted = format_time(time_elapsed) if time_elapsed else "Not recorded"
        
        # Generate workout summary
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Create email content
        if recipient_name:
            greeting = f"Hi {recipient_name},"
        else:
            greeting = "Hi,"
            
        # HTML content for the email
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4A6FA5; color: white; padding: 10px 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ text-align: center; padding: 10px; font-size: 12px; color: #999; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                table, th, td {{ border: 1px solid #ddd; }}
                th, td {{ padding: 12px; text-align: left; }}
                th {{ background-color: #4A6FA5; color: white; }}
                .highlight {{ font-weight: bold; color: #4A6FA5; }}
                .button {{ display: inline-block; background-color: #4A6FA5; color: white; padding: 10px 20px; 
                        text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your AI Personal Trainer Workout</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>
                    <p>Great job on completing your workout! Here's a summary of your performance:</p>
                    
                    <table>
                        <tr>
                            <th colspan="2">Workout Summary</th>
                        </tr>
                        <tr>
                            <td>Date</td>
                            <td>{date_str}</td>
                        </tr>
                        <tr>
                            <td>Duration</td>
                            <td>{time_formatted}</td>
                        </tr>
                        <tr>
                            <td>Calories Burned</td>
                            <td>Approx. {calories} calories</td>
                        </tr>
                    </table>
                    
                    <p>Your workout video is attached to this email. You can review your form and track your progress!</p>
                    
                    <p>Keep up the good work!</p>
                    
                    <p>Best regards,<br>Your AI Personal Trainer</p>
                </div>
                <div class="footer">
                    <p>© {datetime.now().year} AI Personal Trainer. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Your AI Personal Trainer Workout - {date_str}"
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Attach video if provided and valid
        if video_path and os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            print(f"[EmailingSystem] Attaching video: {video_path} ({os.path.getsize(video_path)} bytes)")
            try:
                with open(video_path, 'rb') as f:
                    video_attachment = MIMEBase('application', 'octet-stream')
                    video_attachment.set_payload(f.read())
                    encoders.encode_base64(video_attachment)
                    
                    # Set filename in attachment
                    filename = os.path.basename(video_path)
                    video_attachment.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    msg.attach(video_attachment)
                    print(f"[EmailingSystem] Video attached to email: {filename}")
            except Exception as e:
                print(f"[EmailingSystem] Error attaching video: {e}")
                return False
        else:
            print("[EmailingSystem] No video attached to email (not provided or invalid)")
            # Modify the email content to remove video reference
            html_content = html_content.replace(
                "<p>Your workout video is attached to this email. You can review your form and track your progress!</p>",
                "<p>We couldn't attach your workout video due to technical issues. Please contact support if you need assistance.</p>"
            )
            # Replace the HTML part with updated content
            for part in msg.get_payload():
                if part.get_content_type() == 'text/html':
                    msg.get_payload().remove(part)
                    msg.attach(MIMEText(html_content, 'html'))
                    break
        
        # Connect to SMTP server and send email
        try:
            print(f"[EmailingSystem] Connecting to SMTP server: {smtp_server}:{smtp_port}")
            
            # Resolve the SMTP server hostname first to avoid getaddrinfo failure
            try:
                # Use socket to resolve the hostname
                smtp_ip = socket.gethostbyname(smtp_server)
                print(f"[EmailingSystem] Resolved SMTP server {smtp_server} to IP: {smtp_ip}")
                server = smtplib.SMTP(smtp_ip, smtp_port, timeout=30)
            except socket.gaierror:
                # If hostname resolution fails, try direct IP or fall back to hostname
                print(f"[EmailingSystem] Failed to resolve hostname, trying direct connection")
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            
            server.starttls()
            server.login(sender_email, sender_password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            print(f"[EmailingSystem] Email sent successfully to {recipient_email}")
            return True
        except Exception as e:
            print(f"[EmailingSystem] Error sending email: {e}")
            return False
            
    except Exception as e:
        print(f"[EmailingSystem] Unexpected error in email_user_with_video: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_email_system():
    """Test the email system with sample data"""
    recipient = input("Enter your email address to test: ")
    name = "Test User"
    calories = 250
    time = 1800  # 30 minutes
    
    result = email_user(recipient, name, calories, time, 85)
    
    if result:
        print("Test email sent successfully")
    else:
        print("Failed to send test email")
    
    return result

def send_verification_email(recipient_email, verification_code):
    """Send verification email to user"""
    try:
        print(f"\n[Email System] Preparing verification email for {recipient_email}")
        print(f"[Email System] Verification code: {verification_code}")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'AI Personal Trainer - Verify Your Email'
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email

        # Create the plain text version
        text = f"""
        Welcome to AI Personal Trainer!
        
        Your verification code is: {verification_code}
        
        Please enter this code to verify your email address.
        If you did not request this code, please ignore this email.
        
        Best regards,
        AI Personal Trainer Team
        """

        # Create the HTML version
        html = f"""
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
              .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
              .code {{ font-size: 32px; font-weight: bold; text-align: center; 
                      background-color: #f8f9fa; padding: 20px; margin: 20px 0;
                      border-radius: 8px; letter-spacing: 3px; }}
            </style>
          </head>
          <body>
            <div class="container">
              <h2>Welcome to AI Personal Trainer!</h2>
              <p>Your verification code is:</p>
              <div class="code">{verification_code}</div>
              <p>Please enter this code to verify your email address.</p>
              <p style="color: #666; font-size: 14px;">If you did not request this code, please ignore this email.</p>
            </div>
          </body>
        </html>
        """

        # Record the MIME types
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container
        # The email client will try to render the last part first
        msg.attach(part1)
        msg.attach(part2)

        # Send the message
        return send_smtp_email(recipient_email, msg)
        
    except Exception as e:
        print(f"\n[Email System] Error preparing verification email: {str(e)}")
        print(f"[Email System] Error type: {type(e)}")
        if hasattr(e, '__dict__'):
            print("[Email System] Full error details:", str(e.__dict__))
        return False

def create_verification_email_html(name, verification_code):
    """Create HTML content for verification email"""
    # Greeting
    greeting = f'<p style="font-size:22px; text-align: center;">Welcome {name}!</p>'
    
    # Verification message
    verification_message = '<p style="font-size:20px; text-align: center;"><b>Thank you for registering with AI Personal Trainer</b></p>'
    
    # Verification code
    code_display = f'<p style="font-size:24px; font-weight:bold; text-align: center; background-color:#f2f2f2; padding:15px; margin:20px; border-radius:5px;">{verification_code}</p>'
    
    # Instructions
    instructions = '<p style="font-size:16px; text-align: center;">Please enter this verification code in the app to complete your registration.</p>'
    
    # Additional info
    additional_info = '<p style="font-size:14px; text-align: center;">This code will expire in 30 minutes. If you did not request this verification, please ignore this email.</p>'
    
    # Combine all parts
    return greeting + verification_message + '<p style="font-size:18px; text-align: center;">Your verification code is:</p>' + code_display + instructions + additional_info

def generate_verification_code(length=6):
    """Generate a random verification code of specified length"""
    return ''.join(random.choices(string.digits, k=length))

def send_password_reset_email(recipient_email, reset_code):
    """
    Send a password reset email with a reset code
    
    Args:
        recipient_email: Recipient's email address
        reset_code: The password reset code
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        print(f"Sending password reset email to {recipient_email}")
        
        # Get credentials
        creds = get_email_credentials()
        if not creds:
            return False
            
        # Extract username from email (use first part before @ as name)
        name = recipient_email.split('@')[0]
        
        # Create HTML content
        html_content = create_password_reset_email_html(name, reset_code)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = creds["sender_email"]
        msg['To'] = recipient_email
        msg['Subject'] = "Password Reset Request - PoseFit Trainer"
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send the email
        result = send_smtp_email(recipient_email, msg)
        
        if result:
            print(f"Password reset email sent successfully to {recipient_email}")
        else:
            print(f"Failed to send password reset email to {recipient_email}")
            
        return result
        
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False

def create_password_reset_email_html(name, reset_code):
    """Create HTML content for password reset email"""
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background-color: #f9f9f9;
                border-radius: 5px;
                padding: 20px;
                border: 1px solid #ddd;
            }}
            .header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .code {{
                font-size: 32px;
                text-align: center;
                letter-spacing: 5px;
                font-weight: bold;
                color: #4f46e5;
                padding: 10px;
                margin: 20px 0;
                background-color: #eef2ff;
                border-radius: 5px;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Password Reset Request</h2>
            </div>
            <p>Hello {name},</p>
            <p>We received a request to reset your password for your PoseFit Trainer account. If you didn't make this request, you can safely ignore this email.</p>
            <p>To reset your password, use the following code:</p>
            <div class="code">{reset_code}</div>
            <p>This code will expire in 30 minutes for security reasons.</p>
            <p>If you have any questions, please contact our support team.</p>
            <p>Thank you,<br>The PoseFit Trainer Team</p>
            <div class="footer">
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

if __name__ == "__main__":
    test_email_system()
