import pandas as pd
from pathlib import Path


TICKETS_FILE = Path("data/raw/live_tickets.csv")


DISPUTE_INTENTS = [
    "failed_transaction",
    "double_debit",
    "fraud_alert",
    "card_issue"
]


def is_dispute_case(intent: str) -> bool:
    """
    Determines if a ticket should be treated as a dispute/risk case.
    """

    return intent in DISPUTE_INTENTS


def classify_dispute_type(intent: str) -> str:
    """
    Classifies the dispute type based on ticket intent.
    """

    dispute_map = {
        "failed_transaction": "Failed Transaction Dispute",
        "double_debit": "Double Debit Dispute",
        "fraud_alert": "Fraud/Risk Dispute",
        "card_issue": "Card Service Dispute"
    }

    return dispute_map.get(intent, "Not a Dispute")


def add_dispute_flags_to_tickets():
    """
    Reads live tickets, adds dispute flags,
    updates the ticket file, and returns updated dataframe.
    """

    if not TICKETS_FILE.exists():
        return pd.DataFrame()

    tickets_df = pd.read_csv(TICKETS_FILE)

    if tickets_df.empty:
        return tickets_df

    tickets_df["is_dispute"] = tickets_df["intent"].apply(
        is_dispute_case
    )

    tickets_df["dispute_type"] = tickets_df["intent"].apply(
        classify_dispute_type
    )

    tickets_df.to_csv(TICKETS_FILE, index=False)

    return tickets_df


def get_dispute_summary():
    """
    Returns dispute summary for dashboard KPIs.
    """

    tickets_df = add_dispute_flags_to_tickets()

    if tickets_df.empty:
        return {
            "total_disputes": 0,
            "failed_transaction_disputes": 0,
            "double_debit_disputes": 0,
            "fraud_risk_disputes": 0,
            "card_service_disputes": 0
        }

    return {
        "total_disputes": int(tickets_df["is_dispute"].sum()),
        "failed_transaction_disputes": int(
            (tickets_df["dispute_type"] == "Failed Transaction Dispute").sum()
        ),
        "double_debit_disputes": int(
            (tickets_df["dispute_type"] == "Double Debit Dispute").sum()
        ),
        "fraud_risk_disputes": int(
            (tickets_df["dispute_type"] == "Fraud/Risk Dispute").sum()
        ),
        "card_service_disputes": int(
            (tickets_df["dispute_type"] == "Card Service Dispute").sum()
        )
    }