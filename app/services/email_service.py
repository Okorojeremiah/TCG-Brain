import smtplib
from email.mime.text import MIMEText
from app.utils.config import Config

def send_email(recipient, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = Config.SMTP_SENDER
    msg["To"] = recipient

    with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
        server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
        server.send_message(msg)
