"""
Resolution Engine for the AI Customer Operations Agent.

This module combines:
- customer message
- intent result
- API results
- knowledge base context

Gemini proposes the resolution, then Python validates it against
banking guardrails before returning a final ResolutionResult.
"""

import json
from typing import Any

from app.chatbot.schemas import IntentResult, APICallResult, ResolutionResult
from app.chatbot.model_client import GeminiModelClient


def build_resolution_prompt(
    customer_message: str,
    intent_result: IntentResult,
    api_results: list[APICallResult],
    knowledge_context: str = ""
) -> str:
    """
    Build the prompt Gemini uses to generate a proposed customer resolution.

    Gemini should reason from:
    - customer message
    - detected intent
    - API outputs
    - retrieved knowledge base context

    The output must be structured JSON.
    """

    api_payload = [
        {
            "api_name": result.api_name,
            "function_name": result.function_name,
            "success": result.success,
            "action_completed": result.action_completed,
            "source_system": result.source_system,
            "response": result.response
        }
        for result in api_results
    ]

    prompt = f"""
You are a banking customer operations AI resolution engine.

Your job is to generate a safe, accurate, customer-facing resolution
based ONLY on the provided customer message, intent result, API results,
and knowledge base context.

Do not invent account information, transaction status, fees, timelines,
case IDs, branch details, or actions that are not present in the provided data.

Customer Message:
{customer_message}

Intent Result:
{{
  "intent": "{intent_result.intent}",
  "confidence": {intent_result.confidence},
  "category": "{intent_result.category}",
  "sentiment": "{intent_result.sentiment}",
  "priority": "{intent_result.priority}",
  "requires_api": {str(intent_result.requires_api).lower()},
  "requires_knowledge_base": {str(intent_result.requires_knowledge_base).lower()},
  "requires_escalation": {str(intent_result.requires_escalation).lower()},
  "missing_information": {json.dumps(intent_result.missing_information)},
  "extracted_entities": {json.dumps(intent_result.extracted_entities)}
}}

API Results:
{json.dumps(api_payload, indent=2, ensure_ascii=False)}

Knowledge Base Context:
{knowledge_context if knowledge_context.strip() else "No knowledge base context provided."}

Return ONLY valid JSON in this exact structure:

{{
  "status": "resolved",
  "customer_response": "Clear response to the customer.",
  "assigned_department": "System",
  "priority": "medium",
  "escalation_required": false,
  "escalation_reason": null,
  "actions_taken": [],
  "recommended_next_steps": []
}}

Allowed status values:
- resolved
- needs_follow_up
- escalated
- unresolved

Allowed priority values:
- low
- medium
- high
- critical

Department options:
- Customer Operations
- Finance Operations
- Fraud/Risk Team
- Card Operations
- Digital Banking Support
- Compliance/KYC Team

Rules:
- If required information is missing, status must be "needs_follow_up".
- If an API action failed, do not claim it succeeded.
- If a card was blocked, clearly state that it was blocked.
- If a fraud case was created, mention the case only if the API result contains the case ID.
- If customer asks for general information, answer from knowledge base context.
- If knowledge base context is missing and no API result answers the question, status should be "unresolved".
- Keep the customer response professional, concise, and helpful.
- Do not ask for PIN, password, CVV, OTP, or full card number.
- Never claim an issue has been resolved unless API results confirm resolution.
- If escalation is required by the intent result, set escalation_required to true.
- If status is escalated, assigned_department must not be empty.
- Actions_taken should only contain actions confirmed by API results.
"""

    return prompt.strip()



def generate_resolution(
    customer_message: str,
    intent_result: IntentResult,
    api_results: list[APICallResult],
    knowledge_context: str = "",
    model_client: GeminiModelClient | None = None
) -> dict[str, Any]:
    """
    Ask Gemini to generate a proposed resolution in structured JSON.

    Returns:
        dict[str, Any]: Raw model response from GeminiModelClient.generate_json()
    """

    if model_client is None:
        model_client = GeminiModelClient()

    prompt = build_resolution_prompt(
        customer_message=customer_message,
        intent_result=intent_result,
        api_results=api_results,
        knowledge_context=knowledge_context
    )

    model_response = model_client.generate_json(
        prompt=prompt
    )

    return model_response



def parse_resolution_result(
    model_response: dict[str, Any]
) -> dict[str, Any]:
    """
    Parse Gemini resolution response into a safe dictionary.

    This does not enforce banking rules yet.
    Validation happens in validate_resolution().
    """

    if not model_response.get("success"):
        return {
            "status": "system_error",
            "customer_response": (
                
                "Your request has been received and routed for review. A support officer will follow up with you shortly."
            ),
            "assigned_department": "Customer Operations",
            "priority": "medium",
            "escalation_required": True,
            "escalation_reason": model_response.get("error"),
            "actions_taken": [],
            "recommended_next_steps": [
                "Escalate request for human review"
            ]
        }

    data = model_response.get("data", {})

    return {
        "status": data.get("status", "unresolved"),
        "customer_response": data.get(
            "customer_response",
            "Your request has been received and is being reviewed."
        ),
        "assigned_department": data.get(
            "assigned_department",
            "Customer Operations"
        ),
        "priority": data.get("priority", "medium"),
        "escalation_required": bool(
            data.get("escalation_required", False)
        ),
        "escalation_reason": data.get("escalation_reason"),
        "actions_taken": data.get("actions_taken", []),
        "recommended_next_steps": data.get(
            "recommended_next_steps",
            []
        )
    }


def validate_resolution(
    resolution: dict[str, Any],
    intent_result: IntentResult,
    api_results: list[APICallResult]
) -> dict[str, Any]:
    """
    Apply banking guardrails to Gemini's proposed resolution.

    Gemini proposes.
    Python validates.
    """

    validated = resolution.copy()

    # --------------------------------------------------
    # Missing information
    # --------------------------------------------------

    if intent_result.missing_information:

        validated["status"] = "needs_follow_up"

        if not validated.get(
            "recommended_next_steps"
        ):
            validated["recommended_next_steps"] = []

        for field in intent_result.missing_information:

            step = f"Collect {field}"

            if step not in validated[
                "recommended_next_steps"
            ]:
                validated[
                    "recommended_next_steps"
                ].append(step)

    # --------------------------------------------------
    # Fraud / critical escalation
    # --------------------------------------------------

    if (
        intent_result.requires_escalation
        or intent_result.priority == "critical"
    ):

        validated[
            "escalation_required"
        ] = True

        validated[
            "assigned_department"
        ] = "Fraud/Risk Team"

        if not validated.get(
            "escalation_reason"
        ):
            validated[
                "escalation_reason"
            ] = (
                "Issue requires fraud/risk review."
            )

    # --------------------------------------------------
    # API failures
    # --------------------------------------------------

    api_failure = any(
        result.success is False
        for result in api_results
    )

    if api_failure:

        validated["status"] = "unresolved"

        validated[
            "escalation_required"
        ] = True

        if not validated.get(
            "escalation_reason"
        ):
            validated[
                "escalation_reason"
            ] = (
                "One or more banking services "
                "failed to complete."
            )

    # --------------------------------------------------
    # Department mapping
    # --------------------------------------------------

    if (
        intent_result.category
        == "transaction"
        and not validated[
            "escalation_required"
        ]
    ):
        validated[
            "assigned_department"
        ] = "Finance Operations"

    elif (
        intent_result.category
        == "card"
        and not validated[
            "escalation_required"
        ]
    ):
        validated[
            "assigned_department"
        ] = "Card Operations"

    elif (
        intent_result.category
        == "kyc"
    ):
        validated[
            "assigned_department"
        ] = "Compliance/KYC Team"

    elif (
        intent_result.category
        == "digital_banking"
    ):
        validated[
            "assigned_department"
        ] = (
            "Digital Banking Support"
        )

    # --------------------------------------------------
    # Force priority from intent
    # --------------------------------------------------

    validated[
        "priority"
    ] = intent_result.priority

    return validated


def resolve_customer_request(
    customer_message: str,
    intent_result: IntentResult,
    api_results: list[APICallResult],
    knowledge_context: str = "",
    model_client: GeminiModelClient | None = None
) -> ResolutionResult:
    """
    Main resolution engine entrypoint.

    Flow:
    1. Gemini generates proposed resolution
    2. Parse Gemini output
    3. Python validates banking rules
    4. Return ResolutionResult schema
    """



    # --------------------------------------------------
    # Conversation-first handling
    # --------------------------------------------------

    if intent_result.needs_clarification:

        return ResolutionResult(
            status="needs_follow_up",
            customer_response=(
                intent_result.customer_response
                or intent_result.clarification_question
                or "Could you provide a little more detail?"
            ),
            assigned_department="Customer Operations",
            priority=intent_result.priority,
            escalation_required=False,
            escalation_reason=None,
            actions_taken=[],
            api_results=[]
        )


    model_response = generate_resolution(
        customer_message=customer_message,
        intent_result=intent_result,
        api_results=api_results,
        knowledge_context=knowledge_context,
        model_client=model_client
    )

    parsed_resolution = parse_resolution_result(
        model_response=model_response
    )

    validated_resolution = validate_resolution(
        resolution=parsed_resolution,
        intent_result=intent_result,
        api_results=api_results
    )

    return ResolutionResult(
        status=validated_resolution.get("status", "unresolved"),
        customer_response=validated_resolution.get(
            "customer_response",
            "Your request has been received and is being reviewed."
        ),
        assigned_department=validated_resolution.get(
            "assigned_department",
            "Customer Operations"
        ),
        priority=validated_resolution.get("priority", "medium"),
        escalation_required=bool(
            validated_resolution.get("escalation_required", False)
        ),
        escalation_reason=validated_resolution.get("escalation_reason"),
        actions_taken=validated_resolution.get("actions_taken", []),
        api_results=api_results
    )


if __name__ == "__main__":
    from app.chatbot.intent_engine import detect_intent
    from app.chatbot.api_orchestrator import orchestrate_api_calls

    customer_message = "What is my transfer limit?"

    intent = detect_intent(customer_message)

    api_results = orchestrate_api_calls(
        customer_id="CUST001",
        intent_result=intent
    )

    resolution = resolve_customer_request(
        customer_message=customer_message,
        intent_result=intent,
        api_results=api_results,
        knowledge_context=""
    )

    print(resolution)
