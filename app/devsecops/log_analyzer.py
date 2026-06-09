import pandas as pd
from pathlib import Path


LOG_FILE = Path("data/raw/system_logs.csv")


CRITICAL_KEYWORDS = [
    "timeout",
    "failed authentication",
    "unavailable",
    "latency spike",
    "above threshold",
    "unusual request",
    "upload failed",
    "pipeline failed",
    "integration tests failed",
    "deployment rollback",
    "merge conflict",
    "vulnerability",
    "security",
    "failed",
]


def analyze_log(row) -> dict:
    message = str(row.get("message", "")).lower()
    severity = str(row.get("severity", "Info"))
    event_type = str(row.get("event_type", "System Check"))

    is_incident = False
    incident_type = "Normal"

    if severity in ["Error", "Critical"]:
        is_incident = True

        if event_type == "Pipeline":
            incident_type = "Pipeline Failure"
        elif event_type == "Repository":
            incident_type = "Repository Issue"
        else:
            incident_type = "System Error"

    for keyword in CRITICAL_KEYWORDS:
        if keyword in message:
            is_incident = True

            if "pipeline" in message or "deployment" in message or "tests" in message:
                incident_type = "Pipeline Failure"
            elif "merge" in message or "pull request" in message or "code review" in message:
                incident_type = "Repository Issue"
            elif "authentication" in message or "security" in message or "vulnerability" in message:
                incident_type = "Security Risk"
            elif "database" in message or "timeout" in message:
                incident_type = "Database/Infrastructure Risk"
            else:
                incident_type = "Operational Risk"

    return {
        "is_incident": is_incident,
        "incident_type": incident_type
    }


def analyze_logs() -> pd.DataFrame:
    if not LOG_FILE.exists():
        return pd.DataFrame()

    logs_df = pd.read_csv(LOG_FILE)

    if logs_df.empty:
        return logs_df

    analysis = logs_df.apply(
        analyze_log,
        axis=1,
        result_type="expand"
    )

    logs_df["is_incident"] = analysis["is_incident"]
    logs_df["incident_type"] = analysis["incident_type"]

    logs_df.to_csv(LOG_FILE, index=False)

    return logs_df