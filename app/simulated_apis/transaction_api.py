"""
Simulated Transaction API.

In production, this would connect to the bank's core banking system,
transaction switch, payment processor, dispute system, and reversal service.
"""

from datetime import datetime


TRANSACTION_RECORDS = {
    "CUST001": [
        {
            "transaction_id": "TXN1001",
            "reference": "REF1001",
            "type": "Transfer",
            "amount": 50000,
            "beneficiary_name": "John Musa",
            "beneficiary_bank": "Zenith Bank",
            "beneficiary_account_masked": "203****8891",
            "date": "2026-05-25",
            "status": "Successful",
            "channel": "Mobile App",
            "reversal_status": None,
            "is_duplicate": False,
            "dispute_status": None
        },
        {
            "transaction_id": "TXN1002",
            "reference": "REF1002",
            "type": "POS",
            "amount": 12500,
            "merchant": "Shoprite Ikeja",
            "date": "2026-05-20",
            "status": "Successful",
            "channel": "Card",
            "reversal_status": None,
            "is_duplicate": False,
            "dispute_status": None
        }
    ],
    "CUST002": [
        {
            "transaction_id": "TXN2001",
            "reference": "REF2001",
            "type": "Transfer",
            "amount": 75000,
            "beneficiary_name": "Grace Okon",
            "beneficiary_bank": "GTBank",
            "beneficiary_account_masked": "017****3344",
            "date": "2026-05-27",
            "status": "Failed",
            "channel": "Mobile App",
            "reversal_status": "Pending",
            "is_duplicate": False,
            "dispute_status": None
        },
        {
            "transaction_id": "TXN2002",
            "reference": "REF2002",
            "type": "ATM",
            "amount": 20000,
            "merchant": "UBA ATM",
            "date": "2026-05-18",
            "status": "Failed",
            "channel": "ATM",
            "reversal_status": "Pending",
            "is_duplicate": False,
            "dispute_status": "Open"
        }
    ],
    "CUST003": [
        {
            "transaction_id": "TXN3001",
            "reference": "REF3001",
            "type": "Transfer",
            "amount": 15000,
            "beneficiary_name": "Wrong Beneficiary",
            "beneficiary_bank": "Access Bank",
            "beneficiary_account_masked": "069****4421",
            "date": "2026-05-29",
            "status": "Successful",
            "channel": "Mobile App",
            "reversal_status": None,
            "is_duplicate": False,
            "dispute_status": None
        },
        {
            "transaction_id": "TXN3002",
            "reference": "REF3002",
            "type": "Online Payment",
            "amount": 8000,
            "merchant": "Netflix",
            "date": "2026-05-30",
            "status": "Successful",
            "channel": "Card",
            "reversal_status": None,
            "is_duplicate": True,
            "dispute_status": None
        },
        {
            "transaction_id": "TXN3003",
            "reference": "REF3003",
            "type": "Online Payment",
            "amount": 8000,
            "merchant": "Netflix",
            "date": "2026-05-30",
            "status": "Successful",
            "channel": "Card",
            "reversal_status": "Pending",
            "is_duplicate": True,
            "dispute_status": None
        }
    ]
}


DISPUTE_CASES = {}
RECOVERY_CASES = {}
FRAUD_CASES = {}


def _normalize_customer_id(customer_id: str) -> str:
    return customer_id.strip().upper()


def _not_found_response(customer_id: str) -> dict:
    return {
        "success": False,
        "customer_id": customer_id,
        "message": "Transaction record not found for this customer."
    }


def get_recent_transactions(customer_id: str, limit: int = 5) -> dict:
    """
    Returns recent transactions for a customer.
    """
    customer_id = _normalize_customer_id(customer_id)
    transactions = TRANSACTION_RECORDS.get(customer_id)

    if not transactions:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "transactions": transactions[:limit],
        "message": "Recent transactions retrieved successfully."
    }


def get_transaction_details(customer_id: str, reference: str) -> dict:
    """
    Returns a specific transaction by transaction reference.
    """
    customer_id = _normalize_customer_id(customer_id)
    reference = reference.strip().upper()

    transactions = TRANSACTION_RECORDS.get(customer_id)

    if not transactions:
        return _not_found_response(customer_id)

    for txn in transactions:
        if txn["reference"].upper() == reference:
            return {
                "success": True,
                "customer_id": customer_id,
                "transaction": txn,
                "message": "Transaction details retrieved successfully."
            }

    return {
        "success": False,
        "customer_id": customer_id,
        "reference": reference,
        "message": "Transaction reference not found."
    }


def check_transaction_status(customer_id: str, reference: str) -> dict:
    """
    Returns only transaction status.
    """
    result = get_transaction_details(customer_id, reference)

    if not result.get("success"):
        return result

    txn = result["transaction"]

    return {
        "success": True,
        "customer_id": result["customer_id"],
        "reference": txn["reference"],
        "status": txn["status"],
        "channel": txn["channel"],
        "amount": txn["amount"],
        "message": f"Transaction status is {txn['status']}."
    }


def check_reversal_status(customer_id: str, reference: str) -> dict:
    """
    Checks reversal status for a transaction.
    """
    result = get_transaction_details(customer_id, reference)

    if not result.get("success"):
        return result

    txn = result["transaction"]
    reversal_status = txn.get("reversal_status")

    if not reversal_status:
        reversal_status = "Not Applicable"

    return {
        "success": True,
        "customer_id": result["customer_id"],
        "reference": txn["reference"],
        "transaction_status": txn["status"],
        "reversal_status": reversal_status,
        "message": f"Reversal status is {reversal_status}."
    }


def check_duplicate_debit(customer_id: str, reference: str | None = None) -> dict:
    """
    Checks whether duplicate debit exists.
    If reference is provided, checks similar transactions around that transaction.
    If no reference is provided, scans all transactions for duplicates.
    """
    customer_id = _normalize_customer_id(customer_id)
    transactions = TRANSACTION_RECORDS.get(customer_id)

    if not transactions:
        return _not_found_response(customer_id)

    duplicates = [txn for txn in transactions if txn.get("is_duplicate")]

    if reference:
        reference = reference.strip().upper()
        target_txn = None

        for txn in transactions:
            if txn["reference"].upper() == reference:
                target_txn = txn
                break

        if not target_txn:
            return {
                "success": False,
                "customer_id": customer_id,
                "reference": reference,
                "message": "Transaction reference not found."
            }

        duplicates = [
            txn for txn in transactions
            if txn.get("is_duplicate")
            and txn["amount"] == target_txn["amount"]
            and txn.get("merchant") == target_txn.get("merchant")
        ]

    return {
        "success": True,
        "customer_id": customer_id,
        "duplicate_found": len(duplicates) > 1,
        "duplicates": duplicates,
        "message": (
            "Duplicate debit found."
            if len(duplicates) > 1
            else "No duplicate debit found."
        )
    }


def create_dispute_case(customer_id: str, reference: str, dispute_type: str) -> dict:
    """
    Creates a simulated dispute case.
    """
    customer_id = _normalize_customer_id(customer_id)
    reference = reference.strip().upper()
    
        

    txn_result = get_transaction_details(customer_id, reference)

    if not txn_result.get("success"):
        return txn_result

    case_id = f"DSP-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    txn_result["transaction"]["dispute_status"] = "Open"
    txn_result["transaction"]["dispute_case_id"] = case_id

    DISPUTE_CASES[case_id] = {
        "case_id": case_id,
        "customer_id": customer_id,
        "reference": reference,
        #"reason": reason,
        "dispute_type": dispute_type,
        "status": "Open",
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    return {
        "success": True,
        "case_id": case_id,
        "customer_id": customer_id,
        "reference": reference,
        "status": "Open",
        "message": "Dispute case created successfully.",
        "source_system": "Transaction API",
        "action_completed": True
    }


def create_recovery_case(customer_id: str, reference: str, reason: str = "Wrong beneficiary transfer") -> dict:
    """
    Creates a simulated recovery case for wrong beneficiary transfer.
    """
    customer_id = _normalize_customer_id(customer_id)
    reference = reference.strip().upper()

    txn_result = get_transaction_details(customer_id, reference)

    if not txn_result.get("success"):
        return txn_result

    case_id = f"RCV-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    txn_result["transaction"]["recovery_status"] = "Open"
    txn_result["transaction"]["recovery_case_id"] = case_id

    RECOVERY_CASES[case_id] = {
        "case_id": case_id,
        "customer_id": customer_id,
        "reference": reference,
        "reason": reason,
        "status": "Open",
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    return {
        "success": True,
        "case_id": case_id,
        "customer_id": customer_id,
        "reference": reference,
        "status": "Open",
        "message": "Recovery case created successfully.",
        "source_system": "Transaction API",
        "action_completed": True
    }


def flag_suspicious_transaction(customer_id: str, reference: str) -> dict:
    """
    Flags a transaction as suspicious.
    """
    result = get_transaction_details(customer_id, reference)

    if not result.get("success"):
        return result

    txn = result["transaction"]
    txn["flagged_suspicious"] = True
    txn["flagged_at"] = datetime.now().isoformat(timespec="seconds")

    return {
        "success": True,
        "customer_id": result["customer_id"],
        "reference": reference.upper(),
        "message": "Transaction has been flagged as suspicious.",
        "source_system": "Transaction API",
        "action_completed": True
    }


def create_fraud_case(customer_id: str, reference: str, reason: str = "Unauthorized transaction reported") -> dict:
    """
    Creates a simulated fraud case.
    """
    customer_id = _normalize_customer_id(customer_id)
    reference = reference.strip().upper()

    txn_result = get_transaction_details(customer_id, reference)

    if not txn_result.get("success"):
        return txn_result

    fraud_case_id = f"FRD-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    txn_result["transaction"]["fraud_status"] = "Open"
    txn_result["transaction"]["fraud_case_id"] = fraud_case_id
    FRAUD_CASES[fraud_case_id] = {
        "fraud_case_id": fraud_case_id,
        "customer_id": customer_id,
        "reference": reference,
        "reason": reason,
        "status": "Open",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_system": "Transaction API",
        "action_completed": True
    }

    return {
        "success": True,
        "fraud_case_id": fraud_case_id,
        "customer_id": customer_id,
        "reference": reference,
        "status": "Open",
        "message": "Fraud case created successfully.",
        "source_system": "Transaction API",
        "action_completed": True
    }


def get_dispute_status(case_id: str) -> dict:
    """
    Returns dispute case status.
    """
    case_id = case_id.strip().upper()
    case = DISPUTE_CASES.get(case_id)

    if not case:
        return {
            "success": False,
            "case_id": case_id,
            "message": "Dispute case not found."
        }

    return {
        "success": True,
        "case": case,
        "message": "Dispute status retrieved successfully."
    }


def get_transaction_by_reference(
    customer_id: str,
    reference: str | None = None
) -> dict:
    """
    Retrieves transaction by reference.

    Expected reference format:
        REF1001, REF2001, REF3002, etc.

    If customer provides transaction_id like TXN3002,
    return a friendly validation response instead of crashing.
    """

    customer_id = _normalize_customer_id(customer_id)

    if not reference:
        return {
            "success": False,
            "customer_id": customer_id,
            "requires_follow_up": True,
            "missing_information": ["transaction_reference"],
            "message": (
                "Please provide the transaction reference number. "
                "It should look like REF3002."
            )
        }

    reference = reference.strip().upper()

    if not reference.startswith("REF"):
        return {
            "success": False,
            "customer_id": customer_id,
            "provided_value": reference,
            "requires_follow_up": True,
            "missing_information": ["valid_transaction_reference"],
            "message": (
                "The value provided does not look like a transaction reference. "
                "Please resend the correct reference number. It should look like REF3002."
            )
        }

    return get_transaction_details(
        customer_id=customer_id,
        reference=reference
    )