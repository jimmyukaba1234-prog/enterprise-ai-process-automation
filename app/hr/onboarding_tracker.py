import pandas as pd
from pathlib import Path


ONBOARDING_FILE = Path("data/raw/onboarding_tasks.csv")


def get_onboarding_summary():
    if not ONBOARDING_FILE.exists():
        return {
            "total_onboarding": 0,
            "completed": 0,
            "in_progress": 0,
            "not_started": 0
        }

    df = pd.read_csv(ONBOARDING_FILE)

    return {
        "total_onboarding": len(df),
        "completed": int((df["status"] == "Completed").sum()),
        "in_progress": int((df["status"] == "In Progress").sum()),
        "not_started": int((df["status"] == "Not Started").sum())
    }


def get_pending_tasks():
    if not ONBOARDING_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(ONBOARDING_FILE)

    return df[df["status"] != "Completed"]