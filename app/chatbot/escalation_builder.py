"""
Escalation Builder for the AI Customer Operations Agent.

This module creates a clean escalation summary for cases that
need human review.

It does not decide whether escalation is required.
That decision comes from IntentResult / ResolutionResult.
"""

from typing import Any

from app.chatbot.schemas import (
    AgentResponse,
    EscalationSummary
)

from app.chatbot.model_client import GeminiModelClient


def build_escalation_prompt(
    response: AgentResponse
) -> str:
    """
    Build prompt for Gemini to summarize escalation case.
    """

    return f"""
You are a banking operations escalation assistant.

Create a concise escalation summary for a human support officer.

Customer ID:
{response.customer_id}

Original Customer Message:
{response.original_message}

Detected Intent:
{response.intent}

Sentiment:
{response.sentiment}

Priority:
{response.priority}

Assigned Department:
{response.assigned_department}

Current Status:
{response.status}

AI Customer Response:
{response.customer_response}

APIs Called:
{response.api_called}

Knowledge Sources:
{response.knowledge_sources}

Raw Agent Output:
{response.raw}

Return ONLY valid JSON in this exact structure:

{{
  "summary": "Brief summary of the customer's issue.",
  "actions_taken": [],
  "outstanding_items": [],
  "recommended_next_steps": []
}}

Rules:
- Do not invent facts.
- Do not include PIN, OTP, CVV, passwords, or full card numbers.
- Keep it concise and useful for a human support officer.
- If no API action was completed, say so clearly.
"""


def generate_escalation_summary_text(
    response: AgentResponse,
    model_client: GeminiModelClient | None = None
) -> dict[str, Any]:
    """
    Use Gemini to generate escalation summary fields.
    """

    if model_client is None:
        model_client = GeminiModelClient()

    prompt = build_escalation_prompt(
        response=response
    )

    result = model_client.generate_json(
        prompt=prompt
    )

    if not result.get("success"):
        return {
            "summary": (
                "Customer request requires human review, "
                "but AI summary generation was unavailable."
            ),
            "actions_taken": response.api_called,
            "outstanding_items": [
                "Human officer should review the customer message and agent output."
            ],
            "recommended_next_steps": [
                "Review ticket details",
                "Contact customer if more information is required"
            ]
        }

    data = result.get("data", {})

    return {
        "summary": data.get(
            "summary",
            "Customer request requires human review."
        ),
        "actions_taken": data.get(
            "actions_taken",
            response.api_called
        ),
        "outstanding_items": data.get(
            "outstanding_items",
            []
        ),
        "recommended_next_steps": data.get(
            "recommended_next_steps",
            []
        )
    }


def build_escalation_record(
    response: AgentResponse,
    model_client: GeminiModelClient | None = None
) -> EscalationSummary:
    """
    Build final EscalationSummary dataclass.
    """

    summary_data = generate_escalation_summary_text(
        response=response,
        model_client=model_client
    )

    return EscalationSummary(
        ticket_id=response.ticket_id,
        customer_id=response.customer_id,
        issue_type=response.intent,
        priority=response.priority,
        assigned_department=response.assigned_department,
        summary=summary_data.get("summary", ""),
        actions_taken=summary_data.get("actions_taken", []),
        outstanding_items=summary_data.get("outstanding_items", []),
        recommended_next_steps=summary_data.get("recommended_next_steps", [])
    )


def create_escalation(
    response: AgentResponse,
    model_client: GeminiModelClient | None = None
) -> dict[str, Any]:
    """
    Create escalation package if escalation is required.

    Returns the EscalationSummary dataclass object so other
    services like escalation_notifier.py can use it directly.
    """

    if not response.escalation_required:
        return {
            "success": False,
            "created": False,
            "reason": "Escalation is not required for this response.",
            "escalation": None
        }

    escalation = build_escalation_record(
        response=response,
        model_client=model_client
    )

    return {
        "success": True,
        "created": True,
        "ticket_id": response.ticket_id,
        "assigned_department": response.assigned_department,
        "priority": response.priority,
        "escalation": escalation
    }


if __name__ == "__main__":
    from app.chatbot.agent import process_customer_message
    from app.chatbot.conversation_manager import create_session

    session = create_session(
        customer_id="CUST001"
    )

    agent_response = process_customer_message(
        customer_message="Someone accessed my account without permission",
        customer_id="CUST001",
        session_id=session["session_id"]
    )

    result = create_escalation(
        response=agent_response
    )

    if result["success"]:
        print(result["escalation"])
    else:
        print(result)