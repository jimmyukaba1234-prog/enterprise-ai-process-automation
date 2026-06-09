import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


FALLBACK_TEMPLATES = {
    "Backend Engineer": """
Responsibilities:
- Build scalable backend services
- Develop APIs and integrations
- Maintain databases and system reliability
- Collaborate with frontend and DevOps teams

Requirements:
- Python or Node.js experience
- API development experience
- Database knowledge
- Docker experience
""",

    "Data Analyst": """
Responsibilities:
- Analyze business and operational data
- Build dashboards and reports
- Identify trends and insights
- Support decision-making with analytics

Requirements:
- SQL and Python knowledge
- Dashboard experience
- Strong analytical thinking
"""
}


def generate_job_description(
    role: str,
    department: str = "HR",
    seniority: str = "Mid-level"
) -> str:

    prompt = f"""
Generate a professional job description for Waya Bank.

Role: {role}
Department: {department}
Seniority: {seniority}

Include:
- Job Summary
- Key Responsibilities
- Required Skills
- Preferred Skills
- Experience Requirement
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert HR recruiter."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception:

        return FALLBACK_TEMPLATES.get(
            role,
            "No JD template available."
        )