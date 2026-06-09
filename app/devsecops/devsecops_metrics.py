import pandas as pd
from pathlib import Path


LOG_FILE = Path("data/raw/system_logs.csv")
ALERT_FILE = Path("data/raw/devsecops_alerts.csv")


def get_devsecops_metrics() -> dict:
    logs_df = (
        pd.read_csv(LOG_FILE)
        if LOG_FILE.exists()
        else pd.DataFrame()
    )

    alerts_df = (
        pd.read_csv(ALERT_FILE)
        if ALERT_FILE.exists()
        else pd.DataFrame()
    )

    total_logs = len(logs_df)
    total_alerts = len(alerts_df)

    total_incidents = 0
    critical_logs = 0
    error_logs = 0
    critical_alerts = 0
    escalated_alerts = 0
    pipeline_events = 0
    repository_events = 0
    system_check_events = 0

    if not logs_df.empty:
        if "is_incident" in logs_df.columns:
            total_incidents = int(logs_df["is_incident"].sum())

        critical_logs = int((logs_df["severity"] == "Critical").sum())
        error_logs = int((logs_df["severity"] == "Error").sum())

        if "event_type" in logs_df.columns:
            pipeline_events = int((logs_df["event_type"] == "Pipeline").sum())
            repository_events = int((logs_df["event_type"] == "Repository").sum())
            system_check_events = int((logs_df["event_type"] == "System Check").sum())

    if not alerts_df.empty:
        if "alert_level" in alerts_df.columns:
            critical_alerts = int((alerts_df["alert_level"] == "Critical Alert").sum())

        if "escalation_status" in alerts_df.columns:
            escalated_alerts = int((alerts_df["escalation_status"] == "Escalated").sum())

    return {
        "total_logs": total_logs,
        "total_incidents": total_incidents,
        "critical_logs": critical_logs,
        "error_logs": error_logs,
        "total_alerts": total_alerts,
        "critical_alerts": critical_alerts,
        "escalated_alerts": escalated_alerts,
        "pipeline_events": pipeline_events,
        "repository_events": repository_events,
        "system_check_events": system_check_events
    }


def get_logs_by_service() -> pd.DataFrame:
    if not LOG_FILE.exists():
        return pd.DataFrame()

    logs_df = pd.read_csv(LOG_FILE)

    if logs_df.empty:
        return logs_df

    return (
        logs_df.groupby("service_name")
        .size()
        .reset_index(name="log_count")
        .sort_values(by="log_count", ascending=False)
    )


def get_alert_summary() -> pd.DataFrame:
    if not ALERT_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(ALERT_FILE)


def get_event_type_distribution() -> pd.DataFrame:
    if not LOG_FILE.exists():
        return pd.DataFrame()

    logs_df = pd.read_csv(LOG_FILE)

    if logs_df.empty or "event_type" not in logs_df.columns:
        return pd.DataFrame()

    return (
        logs_df.groupby("event_type")
        .size()
        .reset_index(name="event_count")
        .sort_values(by="event_count", ascending=False)
    )


def get_severity_distribution() -> pd.DataFrame:
    if not LOG_FILE.exists():
        return pd.DataFrame()

    logs_df = pd.read_csv(LOG_FILE)

    if logs_df.empty:
        return pd.DataFrame()

    return (
        logs_df.groupby("severity")
        .size()
        .reset_index(name="severity_count")
    )


def get_incident_type_distribution() -> pd.DataFrame:
    if not LOG_FILE.exists():
        return pd.DataFrame()

    logs_df = pd.read_csv(LOG_FILE)

    if logs_df.empty or "incident_type" not in logs_df.columns:
        return pd.DataFrame()

    incident_df = logs_df[logs_df["incident_type"] != "Normal"]

    return (
        incident_df.groupby("incident_type")
        .size()
        .reset_index(name="incident_count")
        .sort_values(by="incident_count", ascending=False)
    )


def get_escalation_distribution() -> pd.DataFrame:
    if not ALERT_FILE.exists():
        return pd.DataFrame()

    alerts_df = pd.read_csv(ALERT_FILE)

    if alerts_df.empty or "escalation_channel" not in alerts_df.columns:
        return pd.DataFrame()

    return (
        alerts_df.groupby("esc" \
        "alation_channel")
        .size()
        .reset_index(name="alert_count")
        .sort_values(by="alert_count", ascending=False)
    )