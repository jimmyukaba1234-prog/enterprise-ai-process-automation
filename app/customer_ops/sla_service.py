from datetime import datetime
import pandas as pd
from pathlib import Path


TICKETS_FILE = Path("data/raw/live_tickets.csv")


def parse_datetime(date_value):
    """
    Handles different datetime formats from old and new ticket records.
    """

    if pd.isna(date_value):
        return None

    date_text = str(date_value)

    formats = [
        "%Y-%m-%d %I:%M %p",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_text, fmt)
        except ValueError:
            continue

    return None


def calculate_sla_status(sla_deadline: str) -> str:
    deadline = parse_datetime(sla_deadline)

    if deadline is None:
        return "Unknown"

    now = datetime.now()
    time_left = deadline - now
    hours_left = time_left.total_seconds() / 3600

    if hours_left < 0:
        return "Breached"

    if hours_left <= 4:
        return "Approaching Breach"

    return "Within SLA"


def add_sla_status_to_tickets():
    if not TICKETS_FILE.exists():
        return pd.DataFrame()

    tickets_df = pd.read_csv(TICKETS_FILE)

    if tickets_df.empty:
        return tickets_df

    tickets_df["sla_status"] = tickets_df["sla_deadline"].apply(
        calculate_sla_status
    )

    tickets_df.to_csv(TICKETS_FILE, index=False)

    return tickets_df


def get_sla_summary():
    tickets_df = add_sla_status_to_tickets()

    if tickets_df.empty:
        return {
            "total_tickets": 0,
            "within_sla": 0,
            "approaching_breach": 0,
            "breached": 0,
            "unknown": 0
        }

    return {
        "total_tickets": len(tickets_df),
        "within_sla": int((tickets_df["sla_status"] == "Within SLA").sum()),
        "approaching_breach": int((tickets_df["sla_status"] == "Approaching Breach").sum()),
        "breached": int((tickets_df["sla_status"] == "Breached").sum()),
        "unknown": int((tickets_df["sla_status"] == "Unknown").sum())
    }