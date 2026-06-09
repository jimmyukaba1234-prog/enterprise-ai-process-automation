import os
import smtplib

from pathlib import Path
from email.message import EmailMessage

from dotenv import load_dotenv

from app.chatbot.schemas import EscalationSummary


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=True
)


DEPARTMENT_EMAILS = {
    "Fraud/Risk Team": os.getenv("ESCALATION_EMAIL"),
    "Fraud Operations": os.getenv("ESCALATION_EMAIL"),
    "Card Operations": os.getenv("ESCALATION_EMAIL"),
    "Customer Operations": os.getenv("ESCALATION_EMAIL"),
    "Finance Operations": os.getenv("ESCALATION_EMAIL"),
    "Compliance": os.getenv("ESCALATION_EMAIL")
}


def get_department_email(
    department: str
) -> str:

    return (
        DEPARTMENT_EMAILS.get(department)
        or os.getenv("ESCALATION_EMAIL")
    )


def send_escalation_email(
    escalation: EscalationSummary
) -> dict:

    smtp_email = os.getenv(
        "SMTP_EMAIL"
    )

    smtp_password = os.getenv(
        "SMTP_PASSWORD"
    )

    if not smtp_email:
        return {
            "success": False,
            "error": "SMTP_EMAIL missing"
        }

    if not smtp_password:
        return {
            "success": False,
            "error": "SMTP_PASSWORD missing"
        }

    recipient = get_department_email(
        escalation.assigned_department
    )

    subject = (
        f"[{escalation.priority.upper()}] "
        f"{escalation.ticket_id} "
        f"- {escalation.issue_type}"
    )

    body = f"""
AI CUSTOMER OPERATIONS ESCALATION

Ticket ID:
{escalation.ticket_id}

Customer ID:
{escalation.customer_id}

Issue Type:
{escalation.issue_type}

Priority:
{escalation.priority}

Assigned Department:
{escalation.assigned_department}

SUMMARY
--------------------------------

{escalation.summary}

ACTIONS TAKEN
--------------------------------

{chr(10).join(escalation.actions_taken)}

OUTSTANDING ITEMS
--------------------------------

{chr(10).join(escalation.outstanding_items)}

RECOMMENDED NEXT STEPS
--------------------------------

{chr(10).join(escalation.recommended_next_steps)}
"""

    try:

        msg = EmailMessage()

        msg["Subject"] = subject
        msg["From"] = smtp_email
        msg["To"] = recipient

        msg.set_content(body)

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                smtp_email,
                smtp_password
            )

            smtp.send_message(msg)

        return {
            "success": True,
            "recipient": recipient,
            "ticket_id": escalation.ticket_id
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }