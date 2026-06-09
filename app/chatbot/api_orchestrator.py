"""
API Orchestrator for the AI Customer Operations Agent.

This module decides which simulated banking API to call based on
the detected customer intent.
"""

from typing import Any

from app.chatbot.schemas import IntentResult, APICallResult

from app.simulated_apis import customer_api
from app.simulated_apis import card_api
from app.simulated_apis import transaction_api


def build_missing_info_result(
    function_name: str,
    missing_fields: list[str]
) -> APICallResult:
    """
    Return a standard API result when required information is missing.
    """

    return APICallResult(
        api_name="orchestrator",
        function_name=function_name,
        success=False,
        action_completed=False,
        source_system="API Orchestrator",
        response={
            "success": False,
            "action_completed": False,
            "missing_information": missing_fields,
            "message": (
                "Additional information is required before this request "
                "can be processed."
            )
        }
    )


def wrap_api_result(
    api_name: str,
    function_name: str,
    raw_response: dict[str, Any]
) -> APICallResult:
    """
    Convert raw simulated API response into APICallResult schema.
    """

    return APICallResult(
        api_name=api_name,
        function_name=function_name,
        success=bool(raw_response.get("success", False)),
        action_completed=bool(raw_response.get("action_completed", False)),
        source_system=raw_response.get("source_system", api_name),
        response=raw_response
    )


def call_customer_api(
    customer_id: str,
    intent_result: IntentResult
) -> list[APICallResult]:
    """
    Call customer-related simulated APIs based on intent.

    Handles:
    - customer verification
    - KYC status
    - transfer limit
    - account restriction/status
    """

    results = []

    intent = intent_result.intent

    if intent == "kyc_status":
        raw_response = customer_api.get_kyc_status(
            customer_id=customer_id
        )

        results.append(
            wrap_api_result(
                api_name="customer_api",
                function_name="get_kyc_status",
                raw_response=raw_response
            )
        )

    elif intent == "account_limit":
        raw_response = customer_api.get_transfer_limit(
            customer_id=customer_id
        )

        results.append(
            wrap_api_result(
                api_name="customer_api",
                function_name="get_transfer_limit",
                raw_response=raw_response
            )
        )

    elif intent == "account_restriction":
        raw_response = customer_api.get_account_status(
            customer_id=customer_id
        )

        results.append(
            wrap_api_result(
                api_name="customer_api",
                function_name="get_account_status",
                raw_response=raw_response
            )
        )

    else:
        raw_response = customer_api.get_customer_profile(
            customer_id=customer_id
        )

        results.append(
            wrap_api_result(
                api_name="customer_api",
                function_name="get_customer_profile",
                raw_response=raw_response
            )
        )

    return results


def call_card_api(
    customer_id: str,
    intent_result: IntentResult
) -> list[APICallResult]:
    """
    Call card-related simulated APIs based on intent.

    Handles:
    - card status
    - card blocking
    - stolen card report
    - card replacement
    """

    results = []

    intent = intent_result.intent
    card_issue = intent_result.extracted_entities.get("card_issue")

    if intent == "card_status":
        raw_response = card_api.get_card_status(
            customer_id=customer_id
        )

        results.append(
            wrap_api_result(
                api_name="card_api",
                function_name="get_card_status",
                raw_response=raw_response
            )
        )

    elif intent == "card_block":
        if card_issue == "stolen" or intent_result.priority == "critical":
            raw_response = card_api.report_stolen_card(
                customer_id=customer_id
            )

            function_name = "report_stolen_card"

        else:
            raw_response = card_api.block_card(
                customer_id=customer_id,
                reason="Customer requested card block"
            )

            function_name = "block_card"

        results.append(
            wrap_api_result(
                api_name="card_api",
                function_name=function_name,
                raw_response=raw_response
            )
        )

    elif intent == "card_replacement":
        raw_response = card_api.request_card_replacement(
            customer_id=customer_id
        )

        results.append(
            wrap_api_result(
                api_name="card_api",
                function_name="request_card_replacement",
                raw_response=raw_response
            )
        )

    else:
        raw_response = card_api.get_card_details(
            customer_id=customer_id
        )

        results.append(
            wrap_api_result(
                api_name="card_api",
                function_name="get_card_details",
                raw_response=raw_response
            )
        )

    return results


def call_transaction_api(
    customer_id: str,
    intent_result: IntentResult
) -> list[APICallResult]:
    """
    Call transaction-related simulated APIs.

    Handles:
    - double debit
    - failed transfer
    - pending reversal
    - wrong beneficiary
    - unauthorized transaction
    """

    results = []

    entities = intent_result.extracted_entities

    transaction_reference = entities.get(
        "transaction_reference"
    )

    intent = intent_result.intent

    # --------------------------------------------------
    # Missing transaction reference
    # --------------------------------------------------

    if (
        intent in [
            "double_debit",
            "failed_transfer",
            "pending_reversal",
            "unauthorized_transaction"
        ]
        and not transaction_reference
    ):
        return [
            build_missing_info_result(
                function_name=intent,
                missing_fields=[
                    "transaction_reference"
                ]
            )
        ]

    # --------------------------------------------------
    # Transaction lookup
    # --------------------------------------------------

    if transaction_reference:

        lookup_response = (
            transaction_api.get_transaction_by_reference(
                customer_id=customer_id,
                reference=transaction_reference
            )
        )

        results.append(
            wrap_api_result(
                api_name="transaction_api",
                function_name="get_transaction_by_reference",
                raw_response=lookup_response
            )
        )

    # --------------------------------------------------
    # Double Debit
    # --------------------------------------------------

    if intent == "double_debit":

        duplicate_check_response = (
            transaction_api.check_duplicate_debit(
                customer_id=customer_id,
                reference=transaction_reference
            )
        )

        results.append(
            wrap_api_result(
                api_name="transaction_api",
                function_name="check_duplicate_debit",
                raw_response=duplicate_check_response
            )
        )

        if duplicate_check_response.get("duplicate_found"):

            raw_response = (
                transaction_api.create_dispute_case(
                    customer_id=customer_id,
                    reference=transaction_reference,
                    dispute_type="duplicate_debit"
                )
            )

            results.append(
                wrap_api_result(
                    api_name="transaction_api",
                    function_name="create_dispute_case",
                    raw_response=raw_response
                )
            )

        else:

            results.append(
                wrap_api_result(
                    api_name="transaction_api",
                    function_name="check_duplicate_debit",
                    raw_response={
                        "success": False,
                        "action_completed": False,
                        "message": (
                            "No duplicate debit was found for the provided transaction."
                        ),
                        "source_system": "Transaction API"
                    }
                )
            )

       
    # --------------------------------------------------
    # Failed Transfer
    # --------------------------------------------------

    elif intent == "failed_transfer":

        raw_response = (
            transaction_api.check_reversal_status(
                customer_id=customer_id,
                reference=transaction_reference
                #transaction_reference
            )
        )

        results.append(
            wrap_api_result(
                api_name="transaction_api",
                function_name="check_reversal_status",
                raw_response=raw_response
            )
        )

    # --------------------------------------------------
    # Pending Reversal
    # --------------------------------------------------

    elif intent == "pending_reversal":

        raw_response = (
            transaction_api.check_reversal_status(
                customer_id=customer_id,
                reference=transaction_reference
                #transaction_reference
            )
        )

        results.append(
            wrap_api_result(
                api_name="transaction_api",
                function_name="check_reversal_status",
                raw_response=raw_response
            )
        )

    # --------------------------------------------------
    # Wrong Beneficiary
    # --------------------------------------------------

    elif intent == "wrong_beneficiary":

        raw_response = (
            transaction_api.create_recovery_case(
                customer_id=customer_id,
                reference=transaction_reference
            )
        )

        results.append(
            wrap_api_result(
                api_name="transaction_api",
                function_name="create_recovery_case",
                raw_response=raw_response
            )
        )

    # --------------------------------------------------
    # Unauthorized Transaction
    # --------------------------------------------------

    elif intent == "unauthorized_transaction":

        raw_response = (
            transaction_api.create_fraud_case(
                customer_id=customer_id,
                reference=transaction_reference
            )
        )

        results.append(
            wrap_api_result(
                api_name="transaction_api",
                function_name="create_fraud_case",
                raw_response=raw_response
            )
        )

    return results

def orchestrate_api_calls(
    customer_id: str,
    intent_result: IntentResult
) -> list[APICallResult]:
    """
    Main API orchestration entrypoint.

    Decides which simulated banking API or APIs should be called
    based on the detected intent.
    """

    if not intent_result.requires_api:
        return []

    intent = intent_result.intent
    category = intent_result.category

    results = []

    # Always verify customer before sensitive account/card/transaction operations
    if category in ["transaction", "card", "kyc", "account", "complaint"]:
        
    

        verify_response = customer_api.verify_customer(
            customer_id=customer_id
        )

        verification_result = wrap_api_result(
            api_name="customer_api",
            function_name="verify_customer",
            raw_response=verify_response
        )

        results.append(
            verification_result
        )

        if not verification_result.success:
            return results




    if category in ["kyc", "account", "complaint"]:
        results.extend(
            call_customer_api(
                customer_id=customer_id,
                intent_result=intent_result
            )
        )

    elif category == "card":
        results.extend(
            call_card_api(
                customer_id=customer_id,
                intent_result=intent_result
            )
        )

    elif category == "transaction":
        results.extend(
            call_transaction_api(
                customer_id=customer_id,
                intent_result=intent_result
            )
        )

    return results

if __name__ == "__main__":
    from app.chatbot.intent_engine import detect_intent

    intent = detect_intent(
        "What is my transfer limit?"
    )

    results = orchestrate_api_calls(
        customer_id="CUST001",
        intent_result=intent
    )

    for result in results:
        print(result)