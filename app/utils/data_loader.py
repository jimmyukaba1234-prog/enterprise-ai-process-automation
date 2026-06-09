from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")


def load_csv(file_name: str) -> pd.DataFrame:
    file_path = RAW_DIR / file_name

    if not file_path.exists():
        return pd.DataFrame()

    return pd.read_csv(file_path)