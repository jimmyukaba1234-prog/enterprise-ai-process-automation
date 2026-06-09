"""
Intent Engine for the AI Customer Operations Agent.

This module uses Gemini to classify customer complaints,
extract useful entities, detect sentiment, and decide whether
the issue needs APIs, knowledge base retrieval, or escalation.
"""

from app.chatbot.schemas import IntentResult
from app.chatbot.model_client import GeminiModelClient


def build_intent_prompt(
    customer_message: str,
    retrieved_context: str = "",
    conversation_history: str = ""
) -> str:
    """
    Build the prompt used by Gemini to analyze conversation state,
    classify intent, detect missing details, and decide the next action.
    """

    history_section = (
        f"""
Conversation History:
{conversation_history}
"""
        if conversation_history.strip()
        else "Conversation History: No previous conversation provided."
    )

    context_section = (
        f"""
Relevant Knowledge Base Context:
{retrieved_context}
"""
        if retrieved_context.strip()
        else "Relevant Knowledge Base Context: None provided."
    )

    prompt = f"""
You are a conversational banking issue analysis engine for an AI Customer Operations Agent.

Your job is not only to classify the customer's message.

Your job is to:
1. Understand the customer's banking issue.
2. Use the conversation history to understand follow-up replies.
3. Use the knowledge base context when it is relevant.
4. Classify the customer's intent.
5. Extract useful entities and details.
6. Decide what information is still missing.
7. Ask one helpful follow-up question if more detail is needed.
8. Decide whether the issue is ready to resolve.
9. Recommend the next operational action.
10. Generate the next customer-facing response.

You must return ONLY valid JSON.

You must be conversational, calm, professional, and helpful.

Important behavior:
- Do not rush to close the issue.
- For operational complaints, prefer asking useful follow-up questions when key details are missing.
- Ask only ONE follow-up question at a time.
- Do not ask for information the customer already provided in the conversation history.
- Do not ask for PIN, password, OTP, CVV, or full card number.
- If the customer message is vague, ask a clarifying question instead of guessing.
- If the customer has provided enough details, move toward resolution, ticket creation, API action, or escalation.


Multi-turn Conversation Rules:

- Always use Conversation History and Previous Intent State when available.
- If the current message is short, such as "lost", "expired", "yes", "yesterday", "50000", "GTBank", "MTN", "PDF", or "January to March", do not treat it as a new standalone request.
- Interpret short replies as answers to the last assistant question.
- Use previous missing_information to decide what detail the customer just provided.
- If the customer provides one missing detail but more details are still required, ask the next most important follow-up question.
- If the customer provides enough information, set needs_clarification=false and ready_to_resolve=true.
- If the customer response changes the issue, update the intent accordingly.

Examples:
- If previous question asked for card issue type and customer says "lost" or "stolen", classify as card_block, requires_confirmation=true, recommended_action=await_confirmation.
- If previous question asked for card issue type and customer says "expired" or "damaged", classify as card_replacement.
- If previous question asked for amount and customer says "50,000 naira", extract amount and ask for date if date is still missing.
- If previous question asked for statement period and customer says "January to March", extract date period and ask for format if missing.
- If previous question asked for bill provider and customer says "IKEDC", extract provider and ask for meter number if missing.
- If previous question asked for airtime network and customer says "MTN", extract provider and ask for phone number or amount if missing.


Classify the customer's request into one of these intents:

TRANSACTION INTENTS
- failed_transfer
- pending_reversal
- double_debit
- wrong_beneficiary
- unauthorized_transaction

CARD INTENTS
- card_block
- card_replacement
- card_status

ACCOUNT INTENTS
- account_limit
- account_restriction

KYC INTENTS
- kyc_status
- bvn_verification_pending
- account_restriction_inquiry

SERVICE INTENTS
- branch_location
- fees_charges
- digital_banking_help
- complaint_status
- account_statement
- profile_update
- loan_issue
- airtime_data_issue
- bill_payment_issue

CONVERSATIONAL INTENTS
- needs_clarification
- general_inquiry
- unknown

Classify category as one of:

- transaction
- card
- account
- kyc
- branch
- fees
- digital_banking
- complaint
- general
- unknown

Sentiment must be one of:

- positive
- neutral
- negative
- angry
- distressed

Priority must be one of:

- low
- medium
- high
- critical

Recommended Action must be one of:

- ask_customer_question
- retrieve_knowledge
- call_api
- await_confirmation
- create_ticket
- escalate_case
- provide_information
- resolve_issue

Decision Rules:

1. If the customer's issue is vague or incomplete:
   - set needs_clarification = true
   - set ready_to_resolve = false
   - generate a clarification_question

2. If enough information exists to proceed:
   - set needs_clarification = false
   - set ready_to_resolve = true

3. If the customer is responding to a previous question:
   - use conversation history
   - do not treat the message in isolation

4. If information already exists in conversation history:
   - do not ask for it again

5. Ask only ONE clarification question at a time.

6. Do not ask multiple questions in one response.

7. Never invent transaction references, amounts, dates, customer details, or banking information.

8. Never generate a fake resolution.

9. If a fraud, unauthorized transaction, hacked account, stolen card, or security incident is reported:
   - requires_escalation = true
   - priority = critical

10. If the issue requires customer account information:
   - requires_api = true

11. If the issue is informational:
   - requires_knowledge_base = true

12. If the action changes customer data or account state:
   - requires_confirmation = true

13. If the issue can be answered directly from policy or knowledge:
   - recommended_action = provide_information

14. If all required information exists and action can proceed:
   - recommended_action = resolve_issue


   15. Continue the conversation until enough information has been gathered to either:
- provide an answer,
- call an API,
- create a ticket,
- escalate the issue,
- or request confirmation for a sensitive action.

16. Do not stop after receiving one answer if more information is still required.

17. If the customer provides a requested detail, identify the next missing detail and ask for it.

18. If no more information is needed, stop asking questions and proceed to resolution.

19. If sufficient information has been collected to create a support ticket,
stop asking questions and proceed with ticket creation.

20. Do not continue asking questions when the next action should be:
- create_ticket
- call_api
- escalate_case
- await_confirmation

Confirmation Understanding Rules:

Treat the following as confirmation:

- yes
- yes please
- proceed
- go ahead
- confirm
- block it
- do it
- continue
- okay proceed

Treat the following as rejection:

- no
- cancel
- stop
- don't proceed
- never mind
- not now
- ignore it

If a confirmation response is received while awaiting confirmation,
do not ask more questions.
Proceed with the confirmed action.

Required Details By Intent:

failed_transfer:
- amount
- date
- beneficiary name if known

pending_reversal:
- amount
- transaction date

double_debit:
- amount
- transaction date

wrong_beneficiary:
- beneficiary name
- transfer date
- amount

unauthorized_transaction:
- transaction date
- suspicious transaction details

card_block:
- confirmation customer wants card blocked

card_replacement:
- reason for replacement

card_status:
- card issue type such as declined, expired, damaged, captured, blocked, lost, or stolen

kyc_status:
- no additional information usually required

account_limit:
- customer verification may be required through API

branch_location:
- branch name or location if specified

If required information is missing:
- add it to missing_information
- ask one clarification question

Return ONLY valid JSON in this exact structure:

{{
  "intent": "needs_clarification",
  "confidence": 0.0,
  "category": "general",
  "sentiment": "neutral",
  "priority": "medium",
  "requires_api": false,
  "requires_confirmation": false,
  "requires_knowledge_base": true,
  "requires_escalation": false,
  "needs_clarification": true,
  "clarification_question": "",
  "ready_to_resolve": false,
  "recommended_action": "ask_customer_question",
  "customer_response": "",
  "required_entities": [],
  "missing_information": [],
  "extracted_entities": {{
    "transaction_reference": null,
    "amount": null,
    "date": null,
    "merchant": null,
    "beneficiary_name": null,
    "beneficiary_bank": null,
    "card_issue": null,
    "branch_name": null,
    "update_type": null
  }}
}}

Examples:

Customer:
"My card is bad"

Expected:
{{
  "intent": "needs_clarification",
  "confidence": 0.85,
  "category": "card",
  "sentiment": "neutral",
  "priority": "medium",
  "requires_api": false,
  "requires_confirmation": false,
  "requires_knowledge_base": true,
  "requires_escalation": false,
  "needs_clarification": true,
  "clarification_question": "Could you tell me what issue you are experiencing with the card? For example, is it damaged, expired, lost, stolen, or being declined?",
  "ready_to_resolve": false,
  "recommended_action": "ask_customer_question",
  "customer_response": "Could you tell me what issue you are experiencing with the card? For example, is it damaged, expired, lost, stolen, or being declined?",
  "required_entities": ["card_issue"],
  "missing_information": ["card_issue"],
  "extracted_entities": {{
    "transaction_reference": null,
    "amount": null,
    "date": null,
    "merchant": null,
    "beneficiary_name": null,
    "beneficiary_bank": null,
    "card_issue": null,
    "branch_name": null,
    "update_type": null
  }}
}}

Customer:
"My card was stolen"

Expected:
{{
  "intent": "card_block",
  "confidence": 0.95,
  "category": "card",
  "sentiment": "distressed",
  "priority": "critical",
  "requires_api": true,
  "requires_confirmation": true,
  "requires_knowledge_base": true,
  "requires_escalation": true,
  "needs_clarification": false,
  "clarification_question": null,
  "ready_to_resolve": true,
  "recommended_action": "await_confirmation",
  "customer_response": "I understand. For your security, I can help block the card. Please confirm if you would like me to proceed.",
  "required_entities": [],
  "missing_information": [],
  "extracted_entities": {{
    "transaction_reference": null,
    "amount": null,
    "date": null,
    "merchant": null,
    "beneficiary_name": null,
    "beneficiary_bank": null,
    "card_issue": "stolen",
    "branch_name": null,
    "update_type": null
  }}
}}

Customer:
"What is my transfer limit?"

Expected:
{{
  "intent": "account_limit",
  "confidence": 0.95,
  "category": "account",
  "sentiment": "neutral",
  "priority": "medium",
  "requires_api": true,
  "requires_confirmation": false,
  "requires_knowledge_base": true,
  "requires_escalation": false,
  "needs_clarification": false,
  "clarification_question": null,
  "ready_to_resolve": true,
  "recommended_action": "call_api",
  "customer_response": "I can help check your transfer limit.",
  "required_entities": [],
  "missing_information": [],
  "extracted_entities": {{
    "transaction_reference": null,
    "amount": null,
    "date": null,
    "merchant": null,
    "beneficiary_name": null,
    "beneficiary_bank": null,
    "card_issue": null,
    "branch_name": null,
    "update_type": null
  }}
}}

Customer:
"Someone accessed my account without permission"

Expected:
{{
  "intent": "unauthorized_transaction",
  "confidence": 0.95,
  "category": "transaction",
  "sentiment": "distressed",
  "priority": "critical",
  "requires_api": true,
  "requires_confirmation": false,
  "requires_knowledge_base": true,
  "requires_escalation": true,
  "needs_clarification": true,
  "clarification_question": "I'm sorry about that. Please tell me the amount of the unauthorized transaction.",
  "ready_to_resolve": false,
  "recommended_action": "ask_customer_question",
  "customer_response": "I'm sorry about that. Please tell me the amount of the unauthorized transaction.",
  "required_entities": ["amount", "date"],
  "missing_information": ["amount", "date"],
  "extracted_entities": {{
    "transaction_reference": null,
    "amount": null,
    "date": null,
    "merchant": null,
    "beneficiary_name": null,
    "beneficiary_bank": null,
    "card_issue": null,
    "branch_name": null,
    "update_type": null
  }}
}}


Second-turn Conversation Example:

Conversation History:

Customer:
"My transfer failed"

Assistant:
"Could you tell me the amount involved?"

Current Customer Message:
"25000 naira"

Expected:
{{
  "intent": "failed_transfer",
  "confidence": 0.95,
  "category": "transaction",
  "sentiment": "negative",
  "priority": "high",
  "requires_api": true,
  "requires_confirmation": false,
  "requires_knowledge_base": true,
  "requires_escalation": false,
  "needs_clarification": false,
  "clarification_question": null,
  "ready_to_resolve": true,
  "recommended_action": "call_api",
  "customer_response": "Thank you. I now have enough information to check the transfer status.",
  "required_entities": [],
  "missing_information": [],
  "extracted_entities": {{
    "transaction_reference": null,
    "amount": "25000 naira",
    "date": null,
    "merchant": null,
    "beneficiary_name": null,
    "beneficiary_bank": null,
    "card_issue": null,
    "branch_name": null,
    "update_type": null
  }}
}}

Customer:
I was debited but did not receive airtime

Bot:
What network was purchased?

Customer:
MTN

Bot:
What phone number was recharged?

Customer:
080xxxxxxxx

Result:
airtime_data_issue
create_ticket


Customer:
I paid my electricity bill but did not receive a token

Bot:
Which electricity provider?

Customer:
IKEDC

Bot:
What is the meter number?

Customer:
1234567890

Result:
bill_payment_issue
create_ticket



Customer:
My card is bad

Bot:
Is it lost, stolen, damaged, expired, or declined?

Customer:
lost

Bot:
Would you like me to block the card?

Customer:
yes

Result:
card_block
call_api


Customer:
Someone accessed my account

Bot:
How much was involved?

Customer:
50000

Bot:
When did it happen?

Customer:
Yesterday

Result:
unauthorized_transaction
escalate_case
create_ticket

{history_section}

{context_section}

Current Customer Message:
{customer_message}



"""

    return prompt.strip()


def parse_intent_result(
    model_response: dict
) -> IntentResult:
    """
    Convert Gemini JSON response into IntentResult schema.
    """

    if not model_response.get("success"):
        return IntentResult(
            intent="system_error",
            confidence=0.0,
            category="system",
            sentiment="neutral",
            priority="low",
            requires_api=False,
            requires_confirmation=False,
            required_entities=[],
            requires_knowledge_base=False,
            requires_escalation=False,
            needs_clarification=False,
            clarification_question=None,
            ready_to_resolve=False,
            recommended_action="retry_later",
            customer_response=(
                "I'm unable to process your request right now because the AI service is unavailable Please try again later."
            ),
            missing_information=[],
            extracted_entities={
                "error": model_response.get("error")
            }
        )

    data = model_response.get("data", {})

    try:
        raw_confidence = float(
            data.get("confidence", 0.0)
        )
    except (TypeError, ValueError):
        raw_confidence = 0.0

    confidence = max(
        0.0,
        min(raw_confidence, 1.0)
    )

    if confidence < 0.50:
        return IntentResult(
            intent="needs_clarification",
            confidence=confidence,
            category=data.get("category", "general"),
            sentiment=data.get("sentiment", "neutral"),
            priority=data.get("priority", "low"),
            requires_api=False,
            requires_confirmation=False,
            required_entities=[],
            requires_knowledge_base=True,
            requires_escalation=False,
            needs_clarification=True,
            clarification_question=(
                "Could you provide a little more detail about the issue you're experiencing?"
            ),
            ready_to_resolve=False,
            recommended_action="ask_customer_question",
            customer_response=(
                "Could you provide a little more detail about the issue you're experiencing?"
            ),
            missing_information=data.get("missing_information", []),
            extracted_entities=data.get("extracted_entities", {})
        )

    return IntentResult(
        intent=data.get("intent", "needs_clarification"),
        confidence=confidence,
        category=data.get("category", "unknown"),
        sentiment=data.get("sentiment", "neutral"),
        priority=data.get("priority", "medium"),
        requires_api=bool(data.get("requires_api", False)),
        requires_confirmation=bool(
            data.get("requires_confirmation", False)
        ),
        required_entities=data.get(
            "required_entities",
            []
        ),
        requires_knowledge_base=bool(
            data.get("requires_knowledge_base", True)
        ),
        requires_escalation=bool(
            data.get("requires_escalation", False)
        ),
        needs_clarification=bool(
            data.get("needs_clarification", False)
        ),
        clarification_question=data.get(
            "clarification_question"
        ),
        ready_to_resolve=bool(
            data.get("ready_to_resolve", False)
        ),
        recommended_action=data.get(
            "recommended_action"
        ),
        customer_response=data.get(
            "customer_response"
        ),
        missing_information=data.get(
            "missing_information",
            []
        ),
        extracted_entities=data.get(
            "extracted_entities",
            {}
        )
    )




def detect_intent(
    customer_message: str,
    retrieved_context: str = "",
    conversation_history: str = "",
    model_client: GeminiModelClient | None = None
) -> IntentResult:

    """
    Detect customer intent using Gemini.

    Args:
        customer_message: Customer complaint/request.
        retrieved_context: Optional knowledge base context.
        model_client: Optional Gemini client instance.

    Returns:
        IntentResult
    """

    if not customer_message.strip():
        return IntentResult(
            intent="needs_clarification",
            priority="low",
            confidence=0.0,
            category="general",
            sentiment="neutral",
            requires_api=False,
            requires_confirmation=False,
            required_entities=[],
            requires_knowledge_base=False,
            requires_escalation=False,
            needs_clarification=True,
            clarification_question=(
                "Please type your banking issue so I can assist you."
            ),
            ready_to_resolve=False,
            recommended_action="ask_customer_question",
            customer_response=(
                "Please type your banking issue so I can assist you."
            ),
            missing_information=["customer_message"],
            extracted_entities={}
        )

    if model_client is None:
        model_client = GeminiModelClient()

    prompt = build_intent_prompt(
        customer_message=customer_message,
        retrieved_context=retrieved_context,
        conversation_history=conversation_history
    )

    model_response = model_client.generate_json(
        prompt=prompt
    )

    return parse_intent_result(
        model_response=model_response
    )

if __name__ == "__main__":

    test_cases = [
        "I was debited twice yesterday",
        "My ATM card was stolen",
        "I transferred money to the wrong account",
        "What is my transfer limit?",
        "Where is your Ikeja branch?"
    ]

    for case in test_cases:

        print("\n" + "=" * 80)
        print(f"TEST: {case}")

        result = detect_intent(
            customer_message=case
        )

        print(result)