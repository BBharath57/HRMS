# #hwof xigt mrnx yrcl

# """
# email_service.py
# """
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# # --- CONFIGURATION ---
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 465
# # REPLACE THESE WITH YOUR REAL CREDENTIALS
# SENDER_EMAIL = "bharathkumarking143@gmail.com" 
# SENDER_PASSWORD = "hwof xigt mrnx yrcl" 

# def send_email(to, subject, body):
#     """
#     Sends a real email using Gmail SMTP.
#     """
#     try:
#         msg = MIMEMultipart()
#         msg["From"] = SENDER_EMAIL
#         msg["To"] = to
#         msg["Subject"] = subject

#         msg.attach(MIMEText(body, "plain"))

#         # Connect to Gmail Server
#         with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
#             server.login(SENDER_EMAIL, SENDER_PASSWORD)
#             server.sendmail(SENDER_EMAIL, to, msg.as_string())
        
#         print(f"✅ Email sent successfully to {to}")
#         return True

#     except Exception as e:
#         print(f"❌ Failed to send email: {e}")
#         return False



"""
email_service.py
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 #465
# REPLACE THESE WITH YOUR REAL CREDENTIALS
SENDER_EMAIL = "bharathkumarking143@gmail.com" 
SENDER_PASSWORD = "hwof xigt mrnx yrcl"  # App Password

def send_email(to_email, subject, body, cc_emails=None):
    """
    Sends an email with optional CC recipients.
    to_email: string (single email)
    cc_emails: list of strings (['a@b.com', 'c@d.com']) or None
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Handle CC
        recipients = [to_email]
        if cc_emails:
            # Join list into a comma-separated string for the header
            if isinstance(cc_emails, list):
                cc_string = ", ".join(cc_emails)
                recipients.extend(cc_emails)
            else:
                cc_string = cc_emails
                recipients.append(cc_emails)
            
            msg["Cc"] = cc_string

        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail Server
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        
        print(f"✅ Email sent to {to_email} (CC: {cc_emails})")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False