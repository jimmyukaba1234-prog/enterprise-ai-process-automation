import pandas as pd
from pathlib import Path
from app.notifications.devsecops_email_service import send_devsecops_alert_email

LOG_FILE = Path("data/raw/system_logs.csv")
ALERT_FILE = Path("data/raw/devsecops_alerts.csv")

DEVSECOPS_ESCALATION_EMAIL = "juk207752@gmail.com"

def determine_alert_level(row) -> str:
    """
    Determines alert severity level.
    """

    if row["severity"] == "Critical":
        return "Critical Alert"

    if row["severity"] == "Error":
        return "High Alert"

    if row.get("is_incident") is True:
        return "Medium Alert"

    return "No Alert"


def generate_alerts() -> pd.DataFrame:
    """
    Reads analyzed logs and generates operational alerts.
    """

    if not LOG_FILE.exists():
        return pd.DataFrame()

    logs_df = pd.read_csv(LOG_FILE)

    if logs_df.empty:
        return logs_df

    if "is_incident" not in logs_df.columns:
        logs_df["is_incident"] = False

    alerts_df = logs_df.copy()

    alerts_df["alert_level"] = alerts_df.apply(
        determine_alert_level,
        axis=1
    )

    alerts_df = alerts_df[
        alerts_df["alert_level"] != "No Alert"
    ]

    alerts_df["escalation_required"] = alerts_df[
        "alert_level"
    ].isin([
        "Critical Alert",
        "High Alert"
    ])

    alerts_df["escalation_channel"] = alerts_df[
        "alert_level"
    ].map({
        "Critical Alert": "Email + Teams",
        "High Alert": "Email",
        "Medium Alert": "Dashboard"
    })

    alerts_df["escalation_status"] = "Pending"

    for _, row in alerts_df.iterrows():

        if row["alert_level"] == "Critical Alert":

            try:

                send_devsecops_alert_email(
                    to_email=DEVSECOPS_ESCALATION_EMAIL,
                    alert=row.to_dict()
                )

                alerts_df.loc[
                    alerts_df["log_id"] == row["log_id"],
                    "escalation_status"
                ] = "Escalated"

            except Exception as e:

                alerts_df.loc[
                    alerts_df["log_id"] == row["log_id"],
                    "escalation_status"
                ] = f"Failed: {str(e)}"

    alerts_df.to_csv(ALERT_FILE, index=False)

    return alerts_df