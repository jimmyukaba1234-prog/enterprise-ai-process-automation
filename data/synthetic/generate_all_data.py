import pandas as pd
import random
from faker import Faker
from pathlib import Path
from datetime import datetime, timedelta

fake = Faker()

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def random_date(days_back=30):
    return datetime.now() - timedelta(days=random.randint(0, days_back))


def generate_customers(n=120):
    data = []

    for i in range(1, n + 1):
        data.append({
            "customer_id": f"CUST-{i:04d}",
            "full_name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "account_type": random.choice(["Savings", "Current", "Business"]),
            "customer_segment": random.choice(["Retail", "SME", "Premium"]),
            "status": random.choice(["Active", "Inactive", "Restricted"]),
            "created_at": random_date(365)
        })

    pd.DataFrame(data).to_csv(RAW_DIR / "customers.csv", index=False)


def generate_departments():
    departments = [
        ["DEPT-001", "Customer Operations"],
        ["DEPT-002", "Finance Operations"],
        ["DEPT-003", "Compliance/KYC"],
        ["DEPT-004", "Technical Support"],
        ["DEPT-005", "Fraud/Risk Team"],
        ["DEPT-006", "HR"],
        ["DEPT-007", "DevSecOps"],
    ]

    df = pd.DataFrame(departments, columns=["department_id", "department_name"])
    df.to_csv(RAW_DIR / "departments.csv", index=False)


def generate_complaints(n=250):
    customers = pd.read_csv(RAW_DIR / "customers.csv")

    complaint_samples = {
        "Failed Transaction": [
            "I transferred money but the receiver has not gotten it.",
            "My transfer failed but I was debited.",
            "The transaction is pending for hours."
        ],
        "Double Debit": [
            "I was debited twice for one transaction.",
            "My account was charged two times.",
            "I need help with duplicate debit."
        ],
        "Login Issue": [
            "I cannot log into my account.",
            "The app keeps saying invalid login.",
            "I forgot my password and cannot reset it."
        ],
        "KYC Issue": [
            "My KYC verification is still pending.",
            "My uploaded ID was rejected.",
            "I need help completing my KYC."
        ],
        "Card Issue": [
            "My card is not working.",
            "My ATM card transaction failed.",
            "I want to block my card."
        ],
        "App Bug": [
            "The app keeps crashing.",
            "The dashboard is not loading.",
            "I cannot see my transaction history."
        ],
        "Fraud Alert": [
            "I noticed a transaction I did not authorize.",
            "Someone accessed my account.",
            "There is suspicious activity on my account."
        ],
        "General Inquiry": [
            "How do I update my phone number?",
            "How can I upgrade my account?",
            "Where can I find my account statement?"
        ]
    }

    routing = {
        "Failed Transaction": "Finance Operations",
        "Double Debit": "Finance Operations",
        "Login Issue": "Technical Support",
        "KYC Issue": "Compliance/KYC",
        "Card Issue": "Customer Operations",
        "App Bug": "Technical Support",
        "Fraud Alert": "Fraud/Risk Team",
        "General Inquiry": "Customer Operations"
    }

    priority_map = {
        "Failed Transaction": "High",
        "Double Debit": "High",
        "Login Issue": "Medium",
        "KYC Issue": "Medium",
        "Card Issue": "Medium",
        "App Bug": "High",
        "Fraud Alert": "Critical",
        "General Inquiry": "Low"
    }

    data = []

    for i in range(1, n + 1):
        category = random.choice(list(complaint_samples.keys()))
        customer_id = random.choice(customers["customer_id"].tolist())

        data.append({
            "complaint_id": f"CMP-{i:05d}",
            "customer_id": customer_id,
            "complaint_text": random.choice(complaint_samples[category]),
            "category": category,
            "assigned_department": routing[category],
            "priority": priority_map[category],
            "sentiment": random.choice(["Negative", "Neutral", "Positive"]),
            "channel": random.choice(["Chatbot", "Mobile App", "Web App", "WhatsApp"]),
            "created_at": random_date(30)
        })

    pd.DataFrame(data).to_csv(RAW_DIR / "complaints.csv", index=False)


def generate_tickets():
    complaints = pd.read_csv(RAW_DIR / "complaints.csv")
    data = []

    for i, row in complaints.iterrows():
        created_at = pd.to_datetime(row["created_at"])
        status = random.choice(["Open", "In Progress", "Resolved", "Escalated"])
        resolved_at = None

        if status == "Resolved":
            resolved_at = created_at + timedelta(hours=random.randint(1, 72))

        sla_hours = {
            "Critical": 4,
            "High": 24,
            "Medium": 48,
            "Low": 72
        }[row["priority"]]

        data.append({
            "ticket_id": f"TCK-{i+1:05d}",
            "complaint_id": row["complaint_id"],
            "customer_id": row["customer_id"],
            "assigned_department": row["assigned_department"],
            "priority": row["priority"],
            "status": status,
            "sla_deadline": created_at + timedelta(hours=sla_hours),
            "created_at": created_at,
            "resolved_at": resolved_at
        })

    pd.DataFrame(data).to_csv(RAW_DIR / "tickets.csv", index=False)


def generate_chatbot_logs(n=300):
    customers = pd.read_csv(RAW_DIR / "customers.csv")

    intents = [
        "failed_transaction",
        "double_debit",
        "login_issue",
        "kyc_issue",
        "card_issue",
        "app_bug",
        "fraud_alert",
        "general_inquiry"
    ]

    data = []

    for i in range(1, n + 1):
        intent = random.choice(intents)
        escalated = intent in ["failed_transaction", "double_debit", "fraud_alert", "app_bug"]

        data.append({
            "chat_id": f"CHAT-{i:05d}",
            "customer_id": random.choice(customers["customer_id"].tolist()),
            "intent": intent,
            "confidence_score": round(random.uniform(0.65, 0.99), 2),
            "escalated": escalated,
            "bot_resolved": not escalated,
            "created_at": random_date(30)
        })

    pd.DataFrame(data).to_csv(RAW_DIR / "chatbot_logs.csv", index=False)


def generate_hr_data(n=60):

    roles = [
        "Data Analyst",
        "Backend Engineer",
        "Product Manager",
        "Customer Support Officer",
        "DevOps Engineer"
    ]

    role_skills = {
        "Data Analyst": [
            "SQL",
            "Python",
            "Power BI",
            "Excel",
            "Tableau",
            "Data Cleaning"
        ],

        "Backend Engineer": [
            "Python",
            "FastAPI",
            "Django",
            "PostgreSQL",
            "Docker",
            "REST API"
        ],

        "Product Manager": [
            "Roadmapping",
            "User Research",
            "Agile",
            "Jira",
            "Stakeholder Management"
        ],

        "Customer Support Officer": [
            "CRM",
            "Communication",
            "Ticketing",
            "Customer Resolution"
        ],

        "DevOps Engineer": [
            "Docker",
            "CI/CD",
            "GitHub Actions",
            "Linux",
            "Cloud Monitoring",
            "Kubernetes"
        ]
    }

    candidates = []

    for i in range(1, n + 1):

        role = random.choice(roles)

        skills = ", ".join(
            random.sample(role_skills[role], k=3)
        )

        candidates.append({
            "candidate_id": f"CAND-{i:04d}",
            "full_name": fake.name(),
            "role_applied": role,
            "experience_years": random.randint(1, 8),
            "skills_match_score": random.randint(45, 98),
            "skills": skills,
            "ai_rank": random.choice([
                "Strong Match",
                "Moderate Match",
                "Weak Match"
            ]),
            "status": random.choice([
                "Applied",
                "Shortlisted",
                "Interview Scheduled",
                "Rejected",
                "Hired"
            ]),
            "created_at": random_date(30)
        })

    pd.DataFrame(candidates).to_csv(
        RAW_DIR / "hr_candidates.csv",
        index=False
    )

    onboarding = []

    for i in range(1, 31):

        onboarding.append({
            "onboarding_id": f"ONB-{i:04d}",
            "employee_name": fake.name(),
            "role": random.choice(roles),
            "documents_submitted": random.choice([True, False]),
            "training_completed": random.choice([True, False]),
            "account_setup": random.choice([True, False]),
            "status": random.choice([
                "Not Started",
                "In Progress",
                "Completed"
            ]),
            "created_at": random_date(30)
        })

    pd.DataFrame(onboarding).to_csv(
        RAW_DIR / "onboarding_tasks.csv",
        index=False
    )

def generate_devsecops_data(n=200):
    services = ["Auth API", "Payment Service", "Customer API", "KYC Service", "Notification Service"]
    severity = ["Info", "Warning", "Error", "Critical"]

    logs = []

    for i in range(1, n + 1):
        sev = random.choice(severity)

        logs.append({
            "log_id": f"LOG-{i:05d}",
            "service_name": random.choice(services),
            "severity": sev,
            "message": random.choice([
                "Service response time increased",
                "Database connection timeout",
                "Failed authentication attempt detected",
                "Payment API latency spike",
                "KYC document upload failed",
                "Service running normally"
            ]),
            "created_at": random_date(14)
        })

    pd.DataFrame(logs).to_csv(RAW_DIR / "system_logs.csv", index=False)

    health = []

    for service in services:
        health.append({
            "service_name": service,
            "status": random.choice(["Healthy", "Degraded", "Down"]),
            "uptime_percentage": round(random.uniform(95.0, 99.99), 2),
            "avg_response_time_ms": random.randint(80, 900),
            "error_rate_percentage": round(random.uniform(0.1, 7.5), 2),
            "last_checked": datetime.now()
        })

    pd.DataFrame(health).to_csv(RAW_DIR / "service_health.csv", index=False)


def generate_all():
    generate_customers()
    generate_departments()
    generate_complaints()
    generate_tickets()
    generate_chatbot_logs()
    generate_hr_data()
    generate_devsecops_data()

    print("Synthetic data generated successfully in data/raw/")


if __name__ == "__main__":
    generate_all()