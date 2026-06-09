import random
from datetime import datetime
from pathlib import Path

import pandas as pd

LOG_FILE = Path("data/raw/system_logs.csv")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Expanded Services
SERVICES = [
    "Auth API",
    "Payment Service",
    "Customer API",
    "KYC Service",
    "Notification Service",
    "Dashboard Service",
    "CI/CD Pipeline",
    "GitHub Actions",
    "Repository Automation"
]

# Expanded Severities and Event Types
SEVERITIES = [
    "Info",
    "Warning",
    "Error",
    "Critical"
]

EVENT_TYPES = ["System Check", "Pipeline", "Repository"]

# Expanded Messages (Categorized)
SYSTEM_MESSAGES = [
    "Service running normally",
    "Service response time increased",
    "Database connection timeout",
    "Failed authentication attempt detected",
    "Unusual request volume detected",
    "Service unavailable",
    "Security vulnerability found",
    "Deployment completed successfully"
]

PIPELINE_MESSAGES = [
    "Build triggered successfully",
    "Pipeline deployment succeeded",
    "Pipeline failed at testing stage",
    "Unit tests passed successfully",
    "Integration tests failed",
    "Deployment rollback initiated"
]

REPO_MESSAGES = [
    "Pull request created",
    "Merge conflict detected",
    "Code review passed",
    "Code review requested changes",
    "Branch deleted successfully"
]


def generate_log_entry() -> dict:
    event_type = random.choice(EVENT_TYPES)

    if event_type == "System Check":
        message = random.choice(SYSTEM_MESSAGES)
    elif event_type == "Pipeline":
        message = random.choice(PIPELINE_MESSAGES)
    else:
        message = random.choice(REPO_MESSAGES)

    severity = random.choice(SEVERITIES)

    return {
        "log_id": f"LOG-{random.randint(10000, 99999)}",
        "service_name": random.choice(SERVICES),
        "severity": severity,
        "event_type": event_type,
        "message": message,
        "created_at": datetime.now().strftime("%Y-%m-%d %I:%M %p")
    }


def generate_logs(n: int = 50) -> pd.DataFrame:
    logs = [generate_log_entry() for _ in range(n)]

    df = pd.DataFrame(logs)

    if LOG_FILE.exists():
        existing_df = pd.read_csv(LOG_FILE)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_csv(LOG_FILE, index=False)
    return df