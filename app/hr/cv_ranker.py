import pandas as pd
from pathlib import Path


CANDIDATES_FILE = Path(
    "data/raw/hr_candidates.csv"
)


def rank_candidates(role: str):

    if not CANDIDATES_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(CANDIDATES_FILE)

    role_df = df[
        df["role_applied"] == role
    ].copy()

    if role_df.empty:
        return role_df

    role_df["ranking_score"] = (
        role_df["skills_match_score"] * 0.7
        + role_df["experience_years"] * 5
    )

    ranked_df = role_df.sort_values(
        by="ranking_score",
        ascending=False
    )

    return ranked_df[
        [
            "candidate_id",
            "full_name",
            "role_applied",
            "experience_years",
            "skills_match_score",
            "ranking_score",
            "ai_rank",
            "status"
        ]
    ]