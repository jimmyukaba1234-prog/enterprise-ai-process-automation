"""
Simulated Card Management API.

In production, this would connect to the bank's card management system,
card processor, and fraud monitoring system.
"""

from datetime import datetime


CARD_RECORDS = {
    "CUST001": {
        "card_id": "CARD001",
        "customer_id": "CUST001",
        "card_number_masked": "5399********1234",
        "card_type": "Debit",
        "card_scheme": "Mastercard",
        "card_status": "Active",
        "expiry_date": "2028-06",
        "delivery_branch": "Ikeja Branch",
        "replacement_requested": False,
        "replacement_status": None,
        "last_card_transaction": {
            "transaction_id": "CTXN001",
            "type": "POS Payment",
            "amount": 12500,
            "merchant": "Shoprite Ikeja",
            "date": "2026-05-20",
            "status": "Successful"
        }
    },
    "CUST002": {
        "card_id": "CARD002",
        "customer_id": "CUST002",
        "card_number_masked": "5399********5678",
        "card_type": "Debit",
        "card_scheme": "Visa",
        "card_status": "Blocked",
        "expiry_date": "2027-03",
        "delivery_branch": "Victoria Island Branch",
        "replacement_requested": True,
        "replacement_status": "Processing",
        "last_card_transaction": {
            "transaction_id": "CTXN002",
            "type": "ATM Withdrawal",
            "amount": 20000,
            "merchant": "UBA ATM",
            "date": "2026-05-18",
            "status": "Successful"
        }
    },
    "CUST003": {
        "card_id": "CARD003",
        "customer_id": "CUST003",
        "card_number_masked": "5399********9988",
        "card_type": "Debit",
        "card_scheme": "Mastercard",
        "card_status": "Expired",
        "expiry_date": "2025-12",
        "delivery_branch": "Abuja Branch",
        "replacement_requested": False,
        "replacement_status": None,
        "last_card_transaction": {
            "transaction_id": "CTXN003",
            "type": "Online Payment",
            "amount": 8000,
            "merchant": "Netflix",
            "date": "2025-11-15",
            "status": "Successful"
        }
    }
}


def _normalize_customer_id(customer_id: str) -> str:
    return customer_id.strip().upper()


def _not_found_response(customer_id: str) -> dict:
    return {
        "success": False,
        "customer_id": customer_id,
        "message": "Card record not found for this customer."
    }


def get_card_details(customer_id: str) -> dict:
    """
    Returns full card profile for a customer.
    """
    customer_id = _normalize_customer_id(customer_id)
    card = CARD_RECORDS.get(customer_id)

    if not card:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "message": "Card details retrieved successfully.",
        "card": card
    }


def get_card_status(customer_id: str) -> dict:
    """
    Returns the customer's card status.
    """
    customer_id = _normalize_customer_id(customer_id)
    card = CARD_RECORDS.get(customer_id)

    if not card:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "card_id": card["card_id"],
        "card_status": card["card_status"],
        "card_type": card["card_type"],
        "card_scheme": card["card_scheme"],
        "message": f"Card status is {card['card_status']}."
    }


def get_last_card_transaction(customer_id: str) -> dict:
    """
    Returns last card transaction.
    """
    customer_id = _normalize_customer_id(customer_id)
    card = CARD_RECORDS.get(customer_id)

    if not card:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "card_id": card["card_id"],
        "last_card_transaction": card["last_card_transaction"],
        "message": "Last card transaction retrieved successfully."
    }


def check_card_expiry(customer_id: str) -> dict:
    """
    Checks card expiry date and expiry status.
    """
    customer_id = _normalize_customer_id(customer_id)
    card = CARD_RECORDS.get(customer_id)

    if not card:
        return _not_found_response(customer_id)

    expiry_status = "Expired" if card["card_status"] == "Expired" else "Valid"

    return {
        "success": True,
        "customer_id": customer_id,
        "card_id": card["card_id"],
        "expiry_date": card["expiry_date"],
        "expiry_status": expiry_status,
        "message": f"Card expiry status is {expiry_status}."
    }


def get_replacement_status(customer_id: str) -> dict:
    """
    Checks whether customer has requested card replacement.
    """
    customer_id = _normalize_customer_id(customer_id)
    card = CARD_RECORDS.get(customer_id)

    if not card:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "card_id": card["card_id"],
        "replacement_requested": card["replacement_requested"],
        "replacement_status": card["replacement_status"],
        "delivery_branch": card["delivery_branch"],
        "message": (
            "Card replacement has been requested."
            if card["replacement_requested"]
            else "No card replacement request found."
        )
    }


def block_card(customer_id: str, reason: str = "Customer request") -> dict:
    """
    Blocks customer's card.
    """
    customer_id = _normalize_customer_id(customer_id)
    card = CARD_RECORDS.get(customer_id)

    if not card:
        return _not_found_response(customer_id)

    if card["card_status"] == "Blocked":
        return {
            "success": True,
            "customer_id": customer_id,
            "card_id": card["card_id"],
            "message": "Card is already blocked.",
            "card_status": card["card_status"],
            "reason": reason,
            "action_completed": True,
            "source_system": "Card Management API"
        }

    card["card_status"] = "Blocked"
    card["blocked_at"] = datetime.now().isoformat(timespec="seconds")
    card["block_reason"] = reason

    return {
        "success": True,
        "customer_id": customer_id,
        "card_id": card["card_id"],
        "message": "Card has been blocked successfully.",
        "card_status": card["card_status"],
        "reason": reason
    }


def request_card_replacement(customer_id: str) -> dict:
    """
    Initiates card replacement request.
    """
    customer_id = _normalize_customer_id(customer_id)
    card = CARD_RECORDS.get(customer_id)

    if not card:
        return _not_found_response(customer_id)

    if card["replacement_requested"]:
        return {
            "success": True,
            "customer_id": customer_id,
            "card_id": card["card_id"],
            "message": "Card replacement request already exists.",
            "replacement_status": card["replacement_status"],
            "delivery_branch": card["delivery_branch"],
            "action_completed": True,
            "source_system": "Card Management API"
        }

    card["replacement_requested"] = True
    card["replacement_status"] = "Processing"
    card["replacement_requested_at"] = datetime.now().isoformat(timespec="seconds")

    return {
        "success": True,
        "customer_id": customer_id,
        "card_id": card["card_id"],
        "message": "Card replacement request has been initiated.",
        "replacement_status": card["replacement_status"],
        "delivery_branch": card["delivery_branch"],
    }


def report_stolen_card(customer_id: str) -> dict:
    """
    Handles stolen card report:
    - blocks card
    - creates simulated fraud case
    """
    customer_id = _normalize_customer_id(customer_id)
    card = CARD_RECORDS.get(customer_id)

    if not card:
        return _not_found_response(customer_id)

    card["card_status"] = "Blocked"
    card["blocked_at"] = datetime.now().isoformat(timespec="seconds")
    card["block_reason"] = "Stolen card reported"

    fraud_case_id = f"FRD-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return {
        "success": True,
        "customer_id": customer_id,
        "card_id": card["card_id"],
        "message": "Card has been blocked due to stolen card report.",
        "card_status": card["card_status"],
        "fraud_case_created": True,
        "fraud_case_id": fraud_case_id,
        "recommended_next_step": "Customer should request card replacement.",
        "source_system": "Card Management API",
        "action_completed": True
    }