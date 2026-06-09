
import os
from pathlib import Path
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"


load_dotenv(dotenv_path=ENV_PATH, override=True)
print("ENV PATH:", ENV_PATH)
print("SMTP_EMAIL:", os.getenv("SMTP_EMAIL"))

def send_devsecops_alert_email(to_email: str, alert: dict):

    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_email:
        raise ValueError("SMTP_EMAIL is missing from .env")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD is missing from .env")

    subject = f"Critical DevSecOps Alert: {alert['log_id']}"

    body = f"""
Hello,

A critical DevSecOps incident has been detected by the AI Monitoring System.

Log ID: {alert['log_id']}
Service: {alert['service_name']}
Severity: {alert['severity']}
Event Type: {alert.get('event_type', 'Unknown')}
Incident Type: {alert.get('incident_type', 'Unknown')}
Alert Level: {alert.get('alert_level', 'Unknown')}
Created At: {alert['created_at']}

Log Message:
{alert['message']}

AI Incident Summary:
{alert.get('incident_summary', 'No summary available.')}

Recommended Action:
Please investigate the affected service, deployment pipeline,
security activity, infrastructure health, and database connectivity immediately.

Regards,
Waya AI DevSecOps Monitoring System
"""

    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = smtp_email
    msg["To"] = to_email

    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(smtp_email, smtp_password)
        smtp.send_message(msg)