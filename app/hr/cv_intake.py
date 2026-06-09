import pandas as pd
from pathlib import Path


CANDIDATES_FILE = Path("data/raw/hr_candidates.csv")


def load_received_applications():
    """
    Demo CV intake layer.

    In production, this would connect to:
    - HR email inbox
    - ATS API
    - career portal
    - uploaded CV folder

    For this demo, hr_candidates.csv represents received CV/application data.
    """

    if not CANDIDATES_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(CANDIDATES_FILE)

    return df


def get_applications_by_role(role: str):
    """
    Returns applications received for a specific role.
    """

    df = load_received_applications()

    if df.empty:
        return df

    return df[df["role_applied"] == role]


def get_cv_intake_summary():
    """
    Returns summary of received applications.
    """

    df = load_received_applications()

    if df.empty:
        return {
            "total_applications": 0,
            "roles_receiving_applications": 0,
            "new_applications": 0
        }

    return {
        "total_applications": len(df),
        "roles_receiving_applications": df["role_applied"].nunique(),
        "new_applications": int((df["status"] == "Applied").sum())
    }