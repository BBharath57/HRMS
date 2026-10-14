import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body, cc_emails=None):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    # ----------------------------------------------
    # ⚙️ CONFIGURATION FOR RENDER / GMAIL
    # ----------------------------------------------
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # TLS Port (Standard for Cloud)
    timeout_seconds = 5 # 🛑 Don't wait longer than 5s

    if not sender_email or not sender_password:
        print("⚠️ Email credentials missing in Environment.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if cc_emails:
            msg['Cc'] = ", ".join(cc_emails)
            
        msg.attach(MIMEText(body, 'plain'))

        recipients = [to_email] + (cc_emails if cc_emails else [])

        # ----------------------------------------------
        # 🚀 SECURE CONNECTION WITH TIMEOUT
        # ----------------------------------------------
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=timeout_seconds)
        server.set_debuglevel(1)  # Print debug logs to terminal
        
        server.starttls()  # Encrypt the connection
        server.login(sender_email, sender_password)
        
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        
        print(f"✅ Email successfully sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ EMAIL FAILED (App will continue): {e}")
        return False