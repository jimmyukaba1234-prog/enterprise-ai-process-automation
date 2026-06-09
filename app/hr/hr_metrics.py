import pandas as pd
from pathlib import Path


CANDIDATES_FILE = Path(
    "data/raw/hr_candidates.csv"
)

ONBOARDING_FILE = Path(
    "data/raw/onboarding_tasks.csv"
)


def get_hr_metrics():

    metrics = {}

    if CANDIDATES_FILE.exists():

        candidates_df = pd.read_csv(
            CANDIDATES_FILE
        )

        metrics["total_candidates"] = len(
            candidates_df
        )

        metrics["shortlisted_candidates"] = int(
            (
                candidates_df["status"]
                == "Shortlisted"
            ).sum()
        )

        metrics["interviews_scheduled"] = int(
            (
                candidates_df["status"]
                == "Interview Scheduled"
            ).sum()
        )

        metrics["hired_candidates"] = int(
            (
                candidates_df["status"]
                == "Hired"
            ).sum()
        )

    else:
        metrics["total_candidates"] = 0
        metrics["shortlisted_candidates"] = 0
        metrics["interviews_scheduled"] = 0
        metrics["hired_candidates"] = 0

    if ONBOARDING_FILE.exists():

        onboarding_df = pd.read_csv(
            ONBOARDING_FILE
        )

        metrics["completed_onboarding"] = int(
            (
                onboarding_df["status"]
                == "Completed"
            ).sum()
        )

        metrics["pending_onboarding"] = int(
            (
                onboarding_df["status"]
                != "Completed"
            ).sum()
        )

    else:
        metrics["completed_onboarding"] = 0
        metrics["pending_onboarding"] = 0

    return metrics