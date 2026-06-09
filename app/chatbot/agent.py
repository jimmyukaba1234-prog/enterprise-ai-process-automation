from uuid import uuid4

from datetime import datetime
from typing import Any

from app.chatbot.schemas import AgentResponse
from app.chatbot.conversation_manager import (
    get_conversation_history,
    append_message,
    store_last_intent,
    get_last_intent
)

from app.chatbot.knowledge_retriever import (
    semantic_search
)
from app.chatbot.escalation_builder import create_escalation
from app.notifications.email_service import send_escalation_email
#from app.notifications.escalation_notifier import send_escalation_email
from dataclasses import asdict
from app.chatbot.schemas import IntentResult
from app.chatbot.conversation_manager import set_pending_action
from app.chatbot.model_client import (GeminiModelClient)
from app.chatbot.api_orchestrator import orchestrate_api_calls

from app.chatbot.resolution_engine import resolve_customer_request

from app.chatbot.intent_engine import detect_intent
from app.chatbot.conversation_manager import has_pending_action




def generate_ticket_id() -> str:
    """
    Generate a unique ticket ID for customer requests.

    Example:
        TKT-A1B2C3D4
    """

    return f"TKT-{uuid4().hex[:8].upper()}"




def build_agent_response(
    ticket_id: str,
    customer_id: str,
    original_message: str,
    intent: str,
    sentiment: str,
    assigned_department: str,
    priority: str,
    status: str,
    customer_response: str,
    escalation_required: bool = False,
    escalation_summary: str | None = None,
    api_called: list[str] | None = None,
    knowledge_sources: list[str] | None = None,
    raw: dict[str, Any] | None = None
) -> AgentResponse:
    """
    Standardized AgentResponse builder.

    Every execution path inside the agent should
    return through this function.
    """

    return AgentResponse(
        ticket_id=ticket_id,
        customer_id=customer_id,
        original_message=original_message,
        intent=intent,
        sentiment=sentiment,
        assigned_department=assigned_department,
        priority=priority,
        status=status,
        customer_response=customer_response,
        escalation_required=escalation_required,
        escalation_summary=escalation_summary,
        api_called=api_called or [],
        knowledge_sources=knowledge_sources or [],
        created_at=datetime.now().isoformat(
            timespec="seconds"
        ),
        raw=raw or {}
    )




def retrieve_knowledge_context(
    customer_message: str,
    top_k: int = 3
) -> tuple[str, list[str]]:
    """
    Retrieve relevant knowledge base context.

    Agent does NOT decide what the answer is.

    Agent only retrieves context and passes it
    downstream to the intent engine and
    resolution engine.
    """

    try:

        retrieval_result = semantic_search(
            query=customer_message,
            top_k=top_k
        )

        knowledge_context = (
            retrieval_result.combined_context
        )

        knowledge_sources = list(
            {
                chunk.source
                for chunk in retrieval_result.chunks
            }
        )

        return (
            knowledge_context,
            knowledge_sources
        )

    except Exception:
        return "", []
    




def create_pending_action(
    session_id: str,
    customer_id: str,
    intent_result: IntentResult
) -> dict:
    """
    Store a pending customer action that requires confirmation.

    Important:
    The agent does not decide which actions require confirmation.
    That decision comes from intent_result.requires_confirmation.

    This function only stores the action state.
    """

    action_payload = {
        "customer_id": customer_id,
        "intent_result": asdict(intent_result)
    }

    pending_action = set_pending_action(
        session_id=session_id,
        action_name=intent_result.intent,
        action_payload=action_payload,
        confirmation_required=intent_result.requires_confirmation
    )

    return pending_action


def generate_confirmation_message(
    customer_message: str,
    intent_result: IntentResult,
    knowledge_context: str = "",
    model_client: GeminiModelClient | None = None
) -> str:
    """
    Generate a customer confirmation request.

    Agent decides that confirmation is needed.

    Gemini decides how to ask.
    """

    if model_client is None:
        model_client = GeminiModelClient()

    prompt = f"""
You are a professional banking customer support assistant.

The customer has requested an action that requires confirmation before execution.

Customer Message:
{customer_message}

Detected Intent:
{intent_result.intent}

Priority:
{intent_result.priority}

Knowledge Context:
{knowledge_context if knowledge_context else "None"}

Generate a short confirmation request.

Rules:
- Do not say the action has already been completed.
- Do not request PIN, password, OTP, CVV, or full card number.
- Ask the customer to explicitly confirm.
- Be professional and concise.
- Return only the customer-facing message.
"""

    response = model_client.generate_text(
        prompt=prompt
    )

    if response.get("success"):

        text = (
            response.get("text", "")
            .strip()
        )

        if text:
            return text

    return (
        "For security reasons, please confirm whether "
        "you would like me to proceed."
    )

def generate_clarification_question(
    customer_message: str,
    intent_result: IntentResult,
    knowledge_context: str = "",
    model_client: GeminiModelClient | None = None
) -> str:
    """
    Generate a follow-up question when the customer's request is unclear.

    Gemini decides what clarification to ask based on:
    - customer message
    - detected vague intent
    - missing information
    - knowledge base context
    """

    if model_client is None:
        model_client = GeminiModelClient()

    prompt = f"""
You are a professional banking customer support assistant.

The customer's request is unclear or incomplete.

Customer Message:
{customer_message}

Detected Intent:
{intent_result.intent}

Category:
{intent_result.category}

Missing Information:
{intent_result.missing_information}

Required Entities:
{intent_result.required_entities}

Knowledge Context:
{knowledge_context if knowledge_context else "None"}

Generate one helpful clarification question for the customer.

Rules:
- Do not claim the issue is resolved.
- Do not escalate yet unless the message clearly indicates fraud, theft, or urgent risk.
- Ask only for information needed to understand the issue.
- Do not ask for PIN, password, OTP, CVV, or full card number.
- Keep it short and natural.
- If the issue appears to be about a card, ask whether it is lost, stolen, damaged, expired, blocked, captured by ATM, or declining transactions.
- Return only the customer-facing question.
"""

    response = model_client.generate_text(
        prompt=prompt
    )

    if response.get("success"):

        text = response.get("text", "").strip()

        if text:
            return text

    return (
        "Please provide a little more detail so I can understand "
        "the issue and direct it correctly."
    )

from app.chatbot.conversation_manager import (
    get_pending_action,
    clear_pending_action,
    classify_confirmation_intent
)



def process_pending_action(
    customer_message: str,
    customer_id: str,
    session_id: str,
    ticket_id: str,
    model_client: GeminiModelClient | None = None
) -> AgentResponse:
    """
    Process a customer reply to a pending action.

    The agent does not decide the action.
    It only checks confirmation status and executes
    the already stored pending action if confirmed.
    """

    pending_action = get_pending_action(
        session_id=session_id
    )

    if not pending_action:
        return build_agent_response(
            ticket_id=ticket_id,
            customer_id=customer_id,
            original_message=customer_message,
            intent="needs_clarification",
            sentiment="neutral",
            assigned_department="Customer Operations",
            priority="low",
            status="needs_clarification",
            customer_response=(
                "I do not have any pending action to confirm. "
                "Please describe the issue you need help with."
            ),

            escalation_required=False,
            
            #escalation_required=intent_result.requires_escalation,
            raw={
                "reason": "no_pending_action_found"
            }
        )

    confirmation_result = classify_confirmation_intent(
        message=customer_message,
        pending_action=pending_action,
        model_client=model_client
    )

    confirmation_status = confirmation_result.get(
        "confirmation_status",
        "unclear"
    )

    stored_intent = pending_action["action_payload"]["intent_result"]

    intent_result = IntentResult(
        **stored_intent
    )

    if confirmation_status == "rejected":

        clear_pending_action(
            session_id=session_id
        )

        return build_agent_response(
            ticket_id=ticket_id,
            customer_id=customer_id,
            original_message=customer_message,
            intent=intent_result.intent,
            sentiment=intent_result.sentiment,
            assigned_department="Customer Operations",
            priority=intent_result.priority,
            status="cancelled",
            customer_response=(
                "Understood. I have not carried out the requested action."
            ),
            escalation_required=False,
            raw={
                "confirmation_result": confirmation_result,
                "pending_action": pending_action
            }
        )

    

    if confirmation_status == "unclear":

            clarification_message = generate_confirmation_message(
                customer_message=customer_message,
                intent_result=intent_result,
                knowledge_context="",
                model_client=model_client
            )

            
            response = build_agent_response(
                ticket_id=ticket_id,
                customer_id=customer_id,
                original_message=customer_message,
                intent=intent_result.intent,
                sentiment=intent_result.sentiment,
                assigned_department="Customer Operations",
                priority=intent_result.priority,
                status="awaiting_confirmation",
                customer_response=clarification_message,
                escalation_required=False,
                raw={
                    "confirmation_result": confirmation_result,
                    "pending_action": pending_action
                }
            )

            append_message(
                session_id=session_id,
                role="assistant",
                content=response.customer_response
            )

            return response



    api_results = orchestrate_api_calls(
        customer_id=customer_id,
        intent_result=intent_result
    )


    


    successful_action = next(
        (
            result for result in api_results
            if result.success and (
                result.action_completed
                or result.response.get("ticket_id")
                or result.response.get("case_id")
                or result.response.get("assigned_department")
            )
        ),
        None
    )

    
    
    if successful_action:
        response_message = successful_action.response.get(
            "message",
            build_api_success_message(successful_action)
        )

        response = build_agent_response(
            ticket_id=ticket_id,
            customer_id=customer_id,
            original_message=customer_message,
            intent=intent_result.intent,
            sentiment=intent_result.sentiment,
            assigned_department=(
                successful_action.response.get(
                    "assigned_department",
                    "Customer Operations"
                )
            ),
            priority=intent_result.priority,
            status="resolved",
            customer_response=response_message,
            escalation_required=intent_result.requires_escalation,
            escalation_summary=successful_action.response.get(
                "fraud_case_id"
            ),
            api_called=[
                result.function_name
                for result in api_results
            ],
            knowledge_sources=[],
            raw={
                "confirmation_result": confirmation_result,
                "pending_action": pending_action,
                "api_results": [
                    asdict(result)
                    for result in api_results
                ]
            }
        )

        clear_pending_action(
            session_id=session_id
        )

        notification_result = notify_if_escalated(
            response=response,
            model_client=model_client
        )

        response.raw["notification_result"] = (
            notification_result
        )

        append_message(
            session_id=session_id,
            role="assistant",
            content=response.customer_response
        )

        return response





    resolution = resolve_customer_request(
        customer_message=customer_message,
        intent_result=intent_result,
        api_results=api_results,
        knowledge_context="",
        model_client=model_client
    )

    clear_pending_action(
        session_id=session_id
    )

    return build_agent_response(
        ticket_id=ticket_id,
        customer_id=customer_id,
        original_message=customer_message,
        intent=intent_result.intent,
        sentiment=intent_result.sentiment,
        assigned_department=resolution.assigned_department,
        priority=resolution.priority,
        status=resolution.status,
        customer_response=resolution.customer_response,
        escalation_required=resolution.escalation_required,
        escalation_summary=resolution.escalation_reason,
        api_called=[
            result.function_name
            for result in api_results
        ],
        knowledge_sources=[],
        raw={
            "confirmation_result": confirmation_result,
            "pending_action": pending_action,
            "api_results": [
                asdict(result)
                for result in api_results
            ],
            "resolution": asdict(resolution)
        }
    )

def build_api_success_message(api_result) -> str:
    data = api_result.response or {}

    return (
        data.get("message")
        or f"Your request has been logged successfully. "
           f"Ticket ID: {data.get('ticket_id', 'N/A')}. "
           f"Assigned Department: {data.get('assigned_department', 'Customer Operations')}."
    )

def notify_if_escalated(
    response: AgentResponse,
    model_client: GeminiModelClient | None = None
) -> dict:
    if not response.escalation_required:
        return {
            "success": False,
            "reason": "Escalation not required"
        }

    escalation_result = create_escalation(
        response=response,
        model_client=model_client
    )

    if not escalation_result.get("success"):
        return escalation_result

    email_result = send_escalation_email(
        escalation=escalation_result["escalation"]
    )

    return {
        "success": email_result.get("success", False),
        "escalation": escalation_result,
        "email": email_result
    }




def handle_new_request(
    customer_message: str,
    customer_id: str,
    session_id: str,
    ticket_id: str,
    model_client: GeminiModelClient | None = None
) -> AgentResponse:
    """
    Handle a brand new customer request.

    This is the primary orchestration flow.

    No business decisions are made here.

    Agent only coordinates:
    - KB
    - Intent
    - APIs
    - Resolution
    """

    append_message(
        session_id=session_id,
        role="customer",
        content=customer_message
    )


    # ----------------------------------
    # STEP 1
    # Initial Retrieval
    # ----------------------------------

    knowledge_context, knowledge_sources = (
        retrieve_knowledge_context(
            customer_message=customer_message
        )
    )

    # ----------------------------------
    # STEP 2
    # Intent Detection
    # ----------------------------------

    
    history_messages = get_conversation_history(
        session_id=session_id,
        limit=10
    )

    conversation_history = "\n".join(
        [
            f"{msg['role']}: {msg['content']}"
            for msg in history_messages
        ]
    )

    last_intent = get_last_intent(
        session_id=session_id
    )

    if last_intent:
        conversation_history += (
            "\n\nPrevious Intent State:\n"
            f"{last_intent}"
        )


    if last_intent:
        previous_missing = last_intent.get(
            "missing_information",
            []
        )

        message_clean = customer_message.strip().upper()

        if (
            "transaction_reference" in previous_missing
            and message_clean.startswith("TXN")
        ):
            last_intent["missing_information"] = []

            extracted_entities = last_intent.get(
                "extracted_entities",
                {}
            )

            extracted_entities["transaction_reference"] = message_clean

            last_intent["extracted_entities"] = extracted_entities
            last_intent["needs_clarification"] = False
            last_intent["ready_to_resolve"] = True
            last_intent["requires_api"] = True
            last_intent["recommended_action"] = "call_api"

            intent_result = IntentResult(
                **last_intent
            )

            api_results = orchestrate_api_calls(
                customer_id=customer_id,
                intent_result=intent_result
            )

            successful_action = next(
                (
                    result for result in api_results
                    if result.success and (
                        result.action_completed
                        or result.response.get("ticket_id")
                        or result.response.get("case_id")
                        or result.response.get("assigned_department")
                    )
                ),
                None
            )

            if successful_action:
                customer_response = build_api_success_message(successful_action)
                

                response = build_agent_response(
                    ticket_id=ticket_id,
                    customer_id=customer_id,
                    original_message=customer_message,
                    intent=intent_result.intent,
                    sentiment=intent_result.sentiment,
                    assigned_department=(
                        successful_action.response.get(
                            "assigned_department",
                            "Customer Operations"
                        )
                    ),
                    priority=intent_result.priority,
                    status="resolved",
                    customer_response=customer_response,
                    escalation_required=intent_result.requires_escalation,
                    api_called=[
                        result.function_name
                        for result in api_results
                    ],
                    knowledge_sources=[],
                    raw={
                        "intent_result": asdict(intent_result),
                        "api_results": [
                            asdict(result)
                            for result in api_results
                        ]
                    }
                )

                notification_result = notify_if_escalated(
                    response=response,
                    model_client=model_client
                )

                response.raw["notification_result"] = (
                    notification_result
                )

                append_message(
                    session_id=session_id,
                    role="assistant",
                    content=response.customer_response
                )

                return response





    intent_result = detect_intent(
        customer_message=customer_message,
        retrieved_context=knowledge_context,
        conversation_history=conversation_history,
        model_client=model_client
    )
   

    if intent_result.intent == "system_error":

        response = build_agent_response(
            ticket_id=ticket_id,
            customer_id=customer_id,
            original_message=customer_message,
            intent=intent_result.intent,
            sentiment=intent_result.sentiment,
            assigned_department="System",
            priority=intent_result.priority,
            status="system_error",
            customer_response=intent_result.customer_response,
            escalation_required=False,
            knowledge_sources=[],
            raw={
                "intent_result": asdict(intent_result)
            }
        )

        append_message(
            session_id=session_id,
            role="assistant",
            content=response.customer_response
        )

        return response



    # ----------------------------------
    # STEP 3
    # Clarification Flow
    # ----------------------------------

    if intent_result.needs_clarification:

        customer_response = (
            intent_result.customer_response
            or intent_result.clarification_question
            or generate_clarification_question(
                customer_message=customer_message,
                intent_result=intent_result,
                knowledge_context=knowledge_context,
                model_client=model_client
            )
        )

        
        store_last_intent(
            session_id=session_id,
            intent_data=asdict(intent_result)
        )

        response = build_agent_response(
            ticket_id=ticket_id,
            customer_id=customer_id,
            original_message=customer_message,
            intent=intent_result.intent,
            sentiment=intent_result.sentiment,
            assigned_department="Customer Operations",
            priority=intent_result.priority,
            status="needs_clarification",
            customer_response=customer_response,
            escalation_required=False,
            knowledge_sources=knowledge_sources,
            raw={
                "intent_result": asdict(intent_result)
            }
        )

        append_message(
            session_id=session_id,
            role="assistant",
            content=response.customer_response
        )

        return response


    # ----------------------------------
    # STEP 5
    # Confirmation Flow
    # ----------------------------------

    if intent_result.requires_confirmation:

        pending_action = (
            create_pending_action(
                session_id=session_id,
                customer_id=customer_id,
                intent_result=intent_result
            )
        )

        confirmation_message = (
            intent_result.customer_response
            or generate_confirmation_message(
                customer_message=customer_message,
                intent_result=intent_result,
                knowledge_context=knowledge_context,
                model_client=model_client
            )
        )

        response = build_agent_response(
            ticket_id=ticket_id,
            customer_id=customer_id,
            original_message=customer_message,
            intent=intent_result.intent,
            sentiment=intent_result.sentiment,
            assigned_department="Customer Operations",
            priority=intent_result.priority,
            status="awaiting_confirmation",
            customer_response=confirmation_message,
            escalation_required=False,
            knowledge_sources=knowledge_sources,
            raw={
                "intent_result": asdict(intent_result),
                "pending_action": pending_action
            }
        )

        append_message(
            session_id=session_id,
            role="assistant",
            content=response.customer_response
        )

        return response

    # ----------------------------------
    # STEP 6
    # API Execution
    # ----------------------------------

    api_results = []

    if intent_result.requires_api:

        api_results = orchestrate_api_calls(
            customer_id=customer_id,
            intent_result=intent_result
        )

    # ----------------------------------
    # STEP 7
    # Optional Second Retrieval
    # ----------------------------------

    final_context = knowledge_context
    all_sources = knowledge_sources

    if intent_result.requires_knowledge_base:

        secondary_query = (
            f"{intent_result.intent} "
            f"{intent_result.category} "
            f"{' '.join(intent_result.required_entities)}"
        )

        secondary_context, secondary_sources = (
            retrieve_knowledge_context(
                customer_message=secondary_query
            )
        )

        final_context = "\n\n".join(
            [
                knowledge_context,
                secondary_context
            ]
        ).strip()

        all_sources = list(
            set(
                knowledge_sources
                + secondary_sources
            )
        )
    # ----------------------------------
    # STEP 8
    # Resolution Generation
    # ----------------------------------

    

    failed_api_missing_info = next(
        (
            result for result in api_results
            if not result.success
            and result.response.get("missing_information")
        ),
        None
    )

    if failed_api_missing_info:
        missing_items = failed_api_missing_info.response.get(
            "missing_information",
            []
        )

        if "transaction_reference" in missing_items:
            customer_response = (
                "Thank you. Please provide the transaction reference number "
                "so I can complete the investigation."
            )
        else:
            customer_response = (
                "Thank you. I need one more detail to continue: "
                + ", ".join(missing_items)
            )

        response = build_agent_response(
            ticket_id=ticket_id,
            customer_id=customer_id,
            original_message=customer_message,
            intent=intent_result.intent,
            sentiment=intent_result.sentiment,
            assigned_department="Customer Operations",
            priority=intent_result.priority,
            status="needs_clarification",
            customer_response=customer_response,
            escalation_required=False,
            api_called=[
                result.function_name
                for result in api_results
            ],
            knowledge_sources=all_sources,
            raw={
                "intent_result": asdict(intent_result),
                "api_results": [
                    asdict(result)
                    for result in api_results
                ]
            }
        )

        store_last_intent(
            session_id=session_id,
            intent_data=asdict(intent_result)
        )

        append_message(
            session_id=session_id,
            role="assistant",
            content=response.customer_response
        )

        return response


    

    resolution = resolve_customer_request(
        customer_message=customer_message,
        intent_result=intent_result,
        api_results=api_results,
        knowledge_context=final_context,
        model_client=model_client
    )

    # ----------------------------------
    # STEP 9
    # Final Response
    # ----------------------------------

    response = build_agent_response(
        ticket_id=ticket_id,
        customer_id=customer_id,
        original_message=customer_message,
        intent=intent_result.intent,
        sentiment=intent_result.sentiment,
        assigned_department=resolution.assigned_department,
        priority=resolution.priority,
        status=resolution.status,
        customer_response=(
            resolution.customer_response
        ),
        escalation_required=(
            resolution.escalation_required
        ),
        escalation_summary=(
            resolution.escalation_reason
        ),
        api_called=[
            result.function_name
            for result in api_results
        ],
        knowledge_sources=all_sources,
        raw={
            "intent_result": (
                asdict(intent_result)
            ),
            "api_results": [
                asdict(result)
                for result in api_results
            ],
            "resolution": (
                asdict(resolution)
            )
        }
    )

    notification_result = notify_if_escalated(
        response=response,
        model_client=model_client
    )

    response.raw["notification_result"] = (
        notification_result
    )

    append_message(
        session_id=session_id,
        role="assistant",
        content=response.customer_response
    )

    return response



    


def process_customer_message(
    customer_message: str,
    customer_id: str,
    session_id: str,
    model_client: GeminiModelClient | None = None
) -> AgentResponse:
    """
    Main entrypoint for the AI Customer Operations Agent.

    This is the only function the Streamlit UI should call.

    Flow:
    1. Generate ticket ID
    2. Check pending action
    3. If pending action exists, process confirmation/rejection
    4. Otherwise handle as new request
    """

    ticket_id = generate_ticket_id()

    if has_pending_action(
        session_id
    ):

        return process_pending_action(
            customer_message=customer_message,
            customer_id=customer_id,
            session_id=session_id,
            ticket_id=ticket_id,
            model_client=model_client
        )

    return handle_new_request(
        customer_message=customer_message,
        customer_id=customer_id,
        session_id=session_id,
        ticket_id=ticket_id,
        model_client=model_client
    )


if __name__ == "__main__":
    from app.chatbot.conversation_manager import create_session

    session = create_session(
        customer_id="CUST001"
    )

    response = process_customer_message(
        
        customer_message="My card was stolen",
        customer_id="CUST001",
        session_id=session["session_id"]
    )

    print(response)

