
from datetime import datetime
"""
Simulated Customer API.

In production, this would connect to the bank's customer information system,
CRM, KYC platform, and account profile service.
"""

CUSTOMER_RECORDS = {
    "CUST001": {
        "customer_id": "CUST001",
        "full_name": "Ada Johnson",
        "account_number_masked": "012****7890",
        "account_type": "Savings",
        "account_status": "Active",
        "kyc_level": "Tier 3",
        "daily_transfer_limit": 5000000,
        "phone_masked": "080****1234",
        "email_masked": "ada****@email.com",
        "preferred_branch": "Ikeja Branch",
        "risk_status": "Low",
        "digital_support_allowed": True
    },
    "CUST002": {
        "customer_id": "CUST002",
        "full_name": "Tunde Bello",
        "account_number_masked": "023****4567",
        "account_type": "Current",
        "account_status": "Restricted",
        "kyc_level": "Tier 2",
        "daily_transfer_limit": 200000,
        "phone_masked": "081****5678",
        "email_masked": "tun****@email.com",
        "preferred_branch": "Victoria Island Branch",
        "risk_status": "Medium",
        "digital_support_allowed": True,
        "restriction_reason": "Pending KYC document update"
    },
    "CUST003": {
        "customer_id": "CUST003",
        "full_name": "Mary Okafor",
        "account_number_masked": "045****1122",
        "account_type": "Savings",
        "account_status": "Active",
        "kyc_level": "Tier 1",
        "daily_transfer_limit": 50000,
        "phone_masked": "070****8899",
        "email_masked": "mar****@email.com",
        "preferred_branch": "Abuja Branch",
        "risk_status": "Low",
        "digital_support_allowed": True
    }
}


def _normalize_customer_id(customer_id: str) -> str:
    return customer_id.strip().upper()


def _not_found_response(customer_id: str) -> dict:
    return {
        "success": False,
        "customer_id": customer_id,
        "message": "Customer record not found."
    }


def get_customer_profile(customer_id: str) -> dict:
    """
    Returns full customer profile.
    """
    customer_id = _normalize_customer_id(customer_id)
    customer = CUSTOMER_RECORDS.get(customer_id)

    if not customer:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "message": "Customer profile retrieved successfully.",
        "customer": customer
    }


def verify_customer(customer_id: str) -> dict:
    """
    Simulates customer verification using customer ID from a trusted session.
    """
    customer_id = _normalize_customer_id(customer_id)
    customer = CUSTOMER_RECORDS.get(customer_id)

    if not customer:
        return {
            "success": False,
            "verified": False,
            "customer_id": customer_id,
            "message": "Customer could not be verified."
        }

    if not customer.get("digital_support_allowed", False):
        return {
            "success": False,
            "verified": False,
            "customer_id": customer_id,
            "message": "Customer is not allowed to use digital support."
        }

    return {
        "success": True,
        "verified": True,
        "customer_id": customer_id,
        "customer_name": customer["full_name"],
        "account_status": customer["account_status"],
        "kyc_level": customer["kyc_level"],
        "message": "Customer verified successfully."
    }


def get_account_status(customer_id: str) -> dict:
    """
    Returns account status and restriction details.
    """
    customer_id = _normalize_customer_id(customer_id)
    customer = CUSTOMER_RECORDS.get(customer_id)

    if not customer:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "account_status": customer["account_status"],
        "restriction_reason": customer.get("restriction_reason"),
        "message": f"Account status is {customer['account_status']}."
    }


def get_kyc_status(customer_id: str) -> dict:
    """
    Returns customer KYC level and related transfer limit.
    """
    customer_id = _normalize_customer_id(customer_id)
    customer = CUSTOMER_RECORDS.get(customer_id)

    if not customer:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "kyc_level": customer["kyc_level"],
        "daily_transfer_limit": customer["daily_transfer_limit"],
        "message": f"Customer is currently on {customer['kyc_level']}."
    }


def get_transfer_limit(customer_id: str) -> dict:
    """
    Returns customer's daily transfer limit.
    """
    customer_id = _normalize_customer_id(customer_id)
    customer = CUSTOMER_RECORDS.get(customer_id)

    if not customer:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "kyc_level": customer["kyc_level"],
        "daily_transfer_limit": customer["daily_transfer_limit"],
        "message": f"Daily transfer limit is ₦{customer['daily_transfer_limit']:,}."
    }


def get_customer_risk_status(customer_id: str) -> dict:
    """
    Returns customer risk classification.
    """
    customer_id = _normalize_customer_id(customer_id)
    customer = CUSTOMER_RECORDS.get(customer_id)

    if not customer:
        return _not_found_response(customer_id)

    return {
        "success": True,
        "customer_id": customer_id,
        "risk_status": customer["risk_status"],
        "message": f"Customer risk status is {customer['risk_status']}."
    }


def update_contact_request(customer_id: str, update_type: str) -> dict:
    """
    Simulates creating a request to update customer contact/profile information.
    This does not directly update records.
    """
    customer_id = _normalize_customer_id(customer_id)
    customer = CUSTOMER_RECORDS.get(customer_id)

    if not customer:
        return _not_found_response(customer_id)

    allowed_update_types = ["phone", "email", "address"]

    if update_type.lower() not in allowed_update_types:
        return {
            "success": False,
            "customer_id": customer_id,
            "message": "Invalid update type. Allowed values: phone, email, address."
        }


    request_id = f"KYC-UPD-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    return {
        "success": True,
        "customer_id": customer_id,
        "request_id": request_id,
        "update_type": update_type,
        "message": f"{update_type.title()} update request has been created for review.",
        "source_system": "Customer Information API",
        "action_completed": True
    }