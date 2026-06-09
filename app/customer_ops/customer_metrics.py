import pandas as pd
from pathlib import Path


TICKETS_FILE = Path("data/raw/live_tickets.csv")
CHAT_LOGS_FILE = Path("data/raw/live_chatbot_logs.csv")


def load_data():
    tickets_df = pd.read_csv(TICKETS_FILE) if TICKETS_FILE.exists() else pd.DataFrame()
    chats_df = pd.read_csv(CHAT_LOGS_FILE) if CHAT_LOGS_FILE.exists() else pd.DataFrame()

    return tickets_df, chats_df


def get_customer_operations_metrics():
    tickets_df, chats_df = load_data()

    if tickets_df.empty:
        return {
            "total_tickets": 0,
            "open_tickets": 0,
            "escalated_tickets": 0,
            "resolved_tickets": 0,
            "high_priority_tickets": 0,
            "critical_tickets": 0,
            "total_chat_sessions": 0,
            "negative_sentiment_cases": 0,
            "dispute_cases": 0,
            "resolution_rate": 0,
            "average_resolution_time": 0,
            "average_feedback_score": 0
        }

    total_tickets = len(tickets_df)

    open_tickets = int((tickets_df["status"] == "Open").sum())
    escalated_tickets = int((tickets_df["status"] == "Escalated").sum())

    resolved_tickets = 0
    if "resolution_status" in tickets_df.columns:
        resolved_tickets = int((tickets_df["resolution_status"] == "Resolved").sum())

    high_priority_tickets = int((tickets_df["priority"] == "High").sum())
    critical_tickets = int((tickets_df["priority"] == "Critical").sum())
    negative_sentiment_cases = int((tickets_df["sentiment"] == "Negative").sum())

    dispute_cases = 0
    if "is_dispute" in tickets_df.columns:
        dispute_cases = int(tickets_df["is_dispute"].sum())

    total_chat_sessions = len(chats_df)

    resolution_rate = round((resolved_tickets / total_tickets) * 100, 1) if total_tickets else 0

    average_resolution_time = 0
    if "resolution_time_hours" in tickets_df.columns:
        resolution_time = pd.to_numeric(tickets_df["resolution_time_hours"], errors="coerce")
        average_resolution_time = round(resolution_time.mean(), 2) if not resolution_time.dropna().empty else 0

    average_feedback_score = 0
    if "customer_feedback_score" in tickets_df.columns:
        feedback = pd.to_numeric(tickets_df["customer_feedback_score"], errors="coerce")
        average_feedback_score = round(feedback.mean(), 2) if not feedback.dropna().empty else 0

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "escalated_tickets": escalated_tickets,
        "resolved_tickets": resolved_tickets,
        "high_priority_tickets": high_priority_tickets,
        "critical_tickets": critical_tickets,
        "total_chat_sessions": total_chat_sessions,
        "negative_sentiment_cases": negative_sentiment_cases,
        "dispute_cases": dispute_cases,
        "resolution_rate": resolution_rate,
        "average_resolution_time": average_resolution_time,
        "average_feedback_score": average_feedback_score
    }


def get_department_ticket_distribution():
    tickets_df, _ = load_data()

    if tickets_df.empty:
        return pd.DataFrame()

    return (
        tickets_df.groupby("assigned_department")
        .size()
        .reset_index(name="ticket_count")
        .sort_values(by="ticket_count", ascending=False)
    )


def get_priority_distribution():
    tickets_df, _ = load_data()

    if tickets_df.empty:
        return pd.DataFrame()

    return (
        tickets_df.groupby("priority")
        .size()
        .reset_index(name="ticket_count")
    )


def get_sentiment_distribution():
    tickets_df, _ = load_data()

    if tickets_df.empty:
        return pd.DataFrame()

    return (
        tickets_df.groupby("sentiment")
        .size()
        .reset_index(name="ticket_count")
    )


def get_channel_distribution():
    tickets_df, _ = load_data()

    if tickets_df.empty or "channel" not in tickets_df.columns:
        return pd.DataFrame()

    return (
        tickets_df.groupby("channel")
        .size()
        .reset_index(name="ticket_count")
        .sort_values(by="ticket_count", ascending=False)
    )


def get_issue_category_distribution():
    tickets_df, _ = load_data()

    if tickets_df.empty or "issue_category" not in tickets_df.columns:
        return pd.DataFrame()

    return (
        tickets_df.groupby("issue_category")
        .size()
        .reset_index(name="ticket_count")
        .sort_values(by="ticket_count", ascending=False)
    )


def get_customer_segment_distribution():
    tickets_df, _ = load_data()

    if tickets_df.empty or "customer_segment" not in tickets_df.columns:
        return pd.DataFrame()

    return (
        tickets_df.groupby("customer_segment")
        .size()
        .reset_index(name="ticket_count")
        .sort_values(by="ticket_count", ascending=False)
    )


def get_repeat_customer_complaints():
    tickets_df, _ = load_data()

    if tickets_df.empty:
        return pd.DataFrame()

    return (
        tickets_df.groupby("customer_id")
        .size()
        .reset_index(name="complaint_count")
        .sort_values(by="complaint_count", ascending=False)
        .head(10)
    )


def get_resolution_status_distribution():
    tickets_df, _ = load_data()

    if tickets_df.empty or "resolution_status" not in tickets_df.columns:
        return pd.DataFrame()

    return (
        tickets_df.groupby("resolution_status")
        .size()
        .reset_index(name="ticket_count")
        .sort_values(by="ticket_count", ascending=False)
    )


def get_resolution_by_department():
    tickets_df, _ = load_data()

    if tickets_df.empty or "resolution_status" not in tickets_df.columns:
        return pd.DataFrame()

    return (
        tickets_df.groupby(["assigned_department", "resolution_status"])
        .size()
        .reset_index(name="ticket_count")
    )


def get_average_resolution_time_by_department():
    tickets_df, _ = load_data()

    if tickets_df.empty or "resolution_time_hours" not in tickets_df.columns:
        return pd.DataFrame()

    tickets_df["resolution_time_hours"] = pd.to_numeric(
        tickets_df["resolution_time_hours"],
        errors="coerce"
    )

    resolved_df = tickets_df.dropna(subset=["resolution_time_hours"])

    if resolved_df.empty:
        return pd.DataFrame()

    return (
        resolved_df.groupby("assigned_department")["resolution_time_hours"]
        .mean()
        .round(2)
        .reset_index(name="avg_resolution_hours")
        .sort_values(by="avg_resolution_hours", ascending=False)
    )


def get_sla_met_distribution():
    tickets_df, _ = load_data()

    if tickets_df.empty or "sla_met" not in tickets_df.columns:
        return pd.DataFrame()

    sla_df = tickets_df.copy()
    sla_df["sla_met"] = sla_df["sla_met"].astype(str)

    return (
        sla_df.groupby("sla_met")
        .size()
        .reset_index(name="ticket_count")
    )