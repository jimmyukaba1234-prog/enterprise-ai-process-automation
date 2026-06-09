import pandas as pd
from pathlib import Path


LOG_FILE = Path("data/raw/system_logs.csv")


def summarize_incident(row) -> str:
    """
    Creates a simple AI-style incident summary.
    """

    return (
        f"{row['severity']} incident detected on {row['service_name']}. "
        f"Log message: {row['message']}. "
        f"Recommended action: investigate service health, logs, recent deployments, "
        f"database connectivity, and security activity."
    )


def generate_incident_summaries() -> pd.DataFrame:
    """
    Reads analyzed logs and generates incident summaries
    for logs marked as incidents.
    """

    if not LOG_FILE.exists():
        return pd.DataFrame()

    logs_df = pd.read_csv(LOG_FILE)

    if logs_df.empty:
        return logs_df

    if "is_incident" not in logs_df.columns:
        logs_df["is_incident"] = False

    logs_df["incident_summary"] = logs_df.apply(
        lambda row: summarize_incident(row)
        if row["is_incident"] else "",
        axis=1
    )

    logs_df.to_csv(LOG_FILE, index=False)

    return logs_df