"""
Conversation Manager for the AI Customer Operations Agent.

Stores short-term conversation state so the chatbot can handle
multi-turn flows such as:

Customer: My card was stolen
AI: Please confirm if you want me to block the card.
Customer: Yes
AI: Executes pending card block action.

For demo/MVP:
- Uses in-memory storage.

For production:
- Replace CONVERSATION_STORE with PostgreSQL, Redis, or MongoDB.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.chatbot.model_client import GeminiModelClient


CONVERSATION_STORE: dict[str, dict[str, Any]] = {}

MAX_MESSAGES = 100
PENDING_ACTION_TIMEOUT_MINUTES = 30


def generate_session_id() -> str:
    return f"SES-{uuid4().hex[:12].upper()}"


def create_session(
    customer_id: str,
    channel: str = "web_app"
) -> dict[str, Any]:
    session_id = generate_session_id()
    now = datetime.now().isoformat(timespec="seconds")

    session = {
        "session_id": session_id,
        "customer_id": customer_id,
        "channel": channel,
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "pending_action": None,
        "last_intent": None,
        "last_resolution": None,
        "metadata": {}
    }

    CONVERSATION_STORE[session_id] = session

    return session


def get_session(
    session_id: str
) -> dict[str, Any] | None:
    return CONVERSATION_STORE.get(session_id)


def update_session(
    session_id: str,
    updates: dict[str, Any]
) -> dict[str, Any] | None:
    session = get_session(session_id)

    if not session:
        return None

    session.update(updates)
    session["updated_at"] = datetime.now().isoformat(timespec="seconds")

    return session


def append_message(
    session_id: str,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    session = get_session(session_id)

    if not session:
        return None

    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "metadata": metadata or {}
    }

    session["messages"].append(message)

    # Prevent unlimited memory growth.
    session["messages"] = session["messages"][-MAX_MESSAGES:]

    session["updated_at"] = datetime.now().isoformat(timespec="seconds")

    return message


def get_conversation_history(
    session_id: str,
    limit: int = 10
) -> list[dict[str, Any]]:
    session = get_session(session_id)

    if not session:
        return []

    return session["messages"][-limit:]


def set_pending_action(
    session_id: str,
    action_name: str,
    action_payload: dict[str, Any],
    confirmation_required: bool = True
) -> dict[str, Any] | None:
    session = get_session(session_id)

    if not session:
        return None

    pending_action = {
        "action_name": action_name,
        "action_payload": action_payload,
        "confirmation_required": confirmation_required,
        "status": "awaiting_confirmation" if confirmation_required else "ready",
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    session["pending_action"] = pending_action
    session["updated_at"] = datetime.now().isoformat(timespec="seconds")

    return pending_action


def get_pending_action(
    session_id: str
) -> dict[str, Any] | None:
    session = get_session(session_id)

    if not session:
        return None

    return session.get("pending_action")


def is_pending_action_expired(
    pending_action: dict[str, Any]
) -> bool:
    """
    Check whether a pending action has expired.
    """

    if not pending_action:
        return True

    created_at = pending_action.get("created_at")

    if not created_at:
        return True

    created_time = datetime.fromisoformat(
        created_at
    )

    age_minutes = (
        datetime.now() - created_time
    ).total_seconds() / 60

    return (
        age_minutes >
        PENDING_ACTION_TIMEOUT_MINUTES
    )





def has_pending_action(
    session_id: str
) -> bool:

    pending_action = get_pending_action(
        session_id
    )

    if not pending_action:
        return False

    if is_pending_action_expired(
        pending_action
    ):
        clear_pending_action(
            session_id
        )
        return False

    return True


def clear_pending_action(
    session_id: str
) -> None:
    session = get_session(session_id)

    if not session:
        return

    session["pending_action"] = None
    session["updated_at"] = datetime.now().isoformat(timespec="seconds")


def is_confirmation_message(
    message: str
) -> bool:
    """
    Fast fallback confirmation check.

    Use only when a pending action exists.
    """
    normalized = message.strip().lower()

    confirmation_words = {
        "yes",
        "yes please",
        "confirm",
        "confirmed",
        "go ahead",
        "proceed",
        "please proceed",
        "sure",
        "absolutely",
        "that's fine",
        "kindly continue",
        "you may proceed",
        "block it",
        "do it",
        "okay",
        "ok"
    }

    return normalized in confirmation_words


def is_rejection_message(
    message: str
) -> bool:
    """
    Fast fallback rejection check.

    Use only when a pending action exists.
    """
    normalized = message.strip().lower()

    rejection_words = {
        "no",
        "no please",
        "cancel",
        "stop",
        "don't",
        "do not",
        "not now",
        "don't do it",
        "do not proceed"
    }

    return normalized in rejection_words


def classify_confirmation_intent(
    message: str,
    pending_action: dict[str, Any],
    model_client: GeminiModelClient | None = None
) -> dict[str, Any]:
    """
    Use Gemini to classify whether the customer is confirming,
    rejecting, or unclear about a pending action.

    This should only be used when a pending_action exists.
    """

    if not message.strip():
        return {
            "confirmation_status": "unclear",
            "confidence": 0.0,
            "reason": "Empty customer message."
        }

    if is_pending_action_expired(
        pending_action
    ):
        return {
            "confirmation_status": "unclear",
            "confidence": 1.0,
            "reason": "Pending action expired."
        }

    # Fast path first to avoid unnecessary Gemini calls.
    if is_confirmation_message(message):
        return {
            "confirmation_status": "confirmed",
            "confidence": 1.0,
            "reason": "Matched direct confirmation phrase."
        }

    if is_rejection_message(message):
        return {
            "confirmation_status": "rejected",
            "confidence": 1.0,
            "reason": "Matched direct rejection phrase."
        }

    if model_client is None:
        model_client = GeminiModelClient()

    prompt = f"""
You are a banking AI confirmation classifier.

A customer has a pending banking action awaiting confirmation.

Pending Action Name:
{pending_action.get("action_name")}

Pending Action Payload:
{pending_action.get("action_payload")}

Customer Message:
{message}
Classify the customer's message as one of:

- confirmed
- rejected
- unclear

Return ONLY valid JSON in this exact structure:

{{
  "confirmation_status": "confirmed",
  "confidence": 0.0,
  "reason": "Short reason"
}}

Rules:
- "yes", "go ahead", "proceed", "sure", "please continue", "that's fine" should be confirmed.
- "no", "cancel", "don't do it", "stop" should be rejected.
- If the customer asks a new question or says something unrelated, return unclear.
- Do not execute any action. Only classify confirmation intent.
"""

    result = model_client.generate_json(prompt=prompt)

    if not result.get("success"):
        return {
            "confirmation_status": "unclear",
            "confidence": 0.0,
            "reason": result.get("error")
        }

    data = result.get("data", {})

    try:
        confidence = float(data.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(0.0, min(confidence, 1.0))

    status = data.get("confirmation_status", "unclear")

    if status not in {"confirmed", "rejected", "unclear"}:
        status = "unclear"

    return {
        "confirmation_status": status,
        "confidence": confidence,
        "reason": data.get("reason", "")
    }


def store_last_intent(
    session_id: str,
    intent_data: dict[str, Any]
) -> None:
    update_session(
        session_id=session_id,
        updates={
            "last_intent": intent_data
        }
    )

def get_last_intent(
    session_id: str
) -> dict[str, Any] | None:
    session = get_session(session_id)

    if not session:
        return None

    return session.get("last_intent")


def store_last_resolution(
    session_id: str,
    resolution_data: dict[str, Any]
) -> None:
    update_session(
        session_id=session_id,
        updates={
            "last_resolution": resolution_data
        }
    )


if __name__ == "__main__":
    session = create_session(
        customer_id="CUST001"
    )

    print("SESSION:")
    print(session)

    append_message(
        session_id=session["session_id"],
        role="customer",
        content="My card was stolen"
    )

    set_pending_action(
        session_id=session["session_id"],
        action_name="report_stolen_card",
        action_payload={
            "customer_id": "CUST001"
        }
    )

    print("\nPENDING ACTION:")
    print(get_pending_action(session["session_id"]))

    print("\nHAS PENDING ACTION:")
    print(has_pending_action(session["session_id"]))

    print("\nFAST CONFIRMATION CHECK:")
    print(is_confirmation_message("yes"))

    print("\nGEMINI CONFIRMATION CLASSIFIER:")
    print(
        classify_confirmation_intent(
            message="Sure, please proceed",
            pending_action=get_pending_action(session["session_id"])
        )
    )