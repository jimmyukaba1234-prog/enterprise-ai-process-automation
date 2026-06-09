"""
Ticket Writer for the AI Customer Operations Agent.

Writes AgentResponse records to CSV so the existing
dashboard can read customer support activity.

For production:
- Replace CSV with PostgreSQL, SQLite, or a ticketing system.
"""

import csv
import json
from pathlib import Path
from typing import Any

from app.chatbot.schemas import AgentResponse


BASE_DIR = Path(__file__).resolve().parents[2]
TICKET_FILE = BASE_DIR / "data" / "raw" / "live_tickets.csv"


TICKET_COLUMNS = [
    "ticket_id",
    "customer_id",
    "original_message",
    "intent",
    "sentiment",
    "assigned_department",
    "priority",
    "status",
    "customer_response",
    "escalation_required",
    "escalation_summary",
    "api_called",
    "knowledge_sources",
    "created_at",
]


def ensure_ticket_file_exists() -> None:
    """
    Create ticket CSV file with headers if it does not exist.
    """

    TICKET_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not TICKET_FILE.exists():
        with open(
            TICKET_FILE,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=TICKET_COLUMNS
            )
            writer.writeheader()


def serialize_list(
    value: list[Any]
) -> str:
    """
    Safely serialize list values for CSV storage.
    """

    return json.dumps(
        value,
        ensure_ascii=False
    )


def build_ticket_row(
    response: AgentResponse
) -> dict[str, Any]:
    """
    Convert AgentResponse to CSV-safe row.
    """

    return {
        "ticket_id": response.ticket_id,
        "customer_id": response.customer_id,
        "original_message": response.original_message,
        "intent": response.intent,
        "sentiment": response.sentiment,
        "assigned_department": response.assigned_department,
        "priority": response.priority,
        "status": response.status,
        "customer_response": response.customer_response,
        "escalation_required": response.escalation_required,
        "escalation_summary": response.escalation_summary or "",
        "api_called": serialize_list(response.api_called),
        "knowledge_sources": serialize_list(response.knowledge_sources),
        "created_at": response.created_at,
    }


def write_ticket(
    response: AgentResponse
) -> dict[str, Any]:
    """
    Write one AgentResponse to live_tickets.csv.
    """

    try:
        ensure_ticket_file_exists()

        row = build_ticket_row(
            response=response
        )

        with open(
            TICKET_FILE,
            mode="a",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=TICKET_COLUMNS
            )
            writer.writerow(row)

        return {
            "success": True,
            "ticket_id": response.ticket_id,
            "path": str(TICKET_FILE),
            "row": row,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "ticket_id": response.ticket_id,
            "path": str(TICKET_FILE),
            "row": None,
            "error": str(e)
        }


if __name__ == "__main__":
    from app.chatbot.agent import process_customer_message
    from app.chatbot.conversation_manager import create_session

    session = create_session(
        customer_id="CUST001"
    )

    agent_response = process_customer_message(
        customer_message="What is my transfer limit?",
        customer_id="CUST001",
        session_id=session["session_id"]
    )

    result = write_ticket(
        response=agent_response
    )

    print(result)