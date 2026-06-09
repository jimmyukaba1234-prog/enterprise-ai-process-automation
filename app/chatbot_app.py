import streamlit as st
from dataclasses import asdict

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.chatbot.agent import process_customer_message
from app.chatbot.conversation_manager import create_session

from app.chatbot.ticket_writer import write_ticket
from app.chatbot.escalation_builder import create_escalation
from app.notifications.email_service import send_escalation_email


st.set_page_config(
    page_title="AI Customer Support",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)


st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display: none !important;
    }

    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(34,197,94,0.18), transparent 28%),
            radial-gradient(circle at bottom right, rgba(16,185,129,0.12), transparent 25%),
            linear-gradient(135deg, #020617 0%, #052e16 55%, #064e3b 100%);
    }

    .main .block-container {
        padding-top: 2rem;
        max-width: 850px;
    }

    .chat-title {
        font-size: 36px;
        font-weight: 900;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 4px;
        letter-spacing: -0.8px;
    }

    .green-line {
        width: 90px;
        height: 5px;
        background: linear-gradient(90deg, #22C55E, #86EFAC);
        border-radius: 30px;
        margin: 0 auto 14px auto;
        box-shadow: 0px 0px 18px rgba(34,197,94,0.35);
    }

    .chat-subtitle {
        font-size: 14px;
        color: #D1FAE5;
        text-align: center;
        margin-bottom: 24px;
        line-height: 1.6;
    }

    .meta-box {
        background: rgba(15,23,42,0.72);
        border: 1px solid rgba(134,239,172,0.18);
        border-radius: 14px;
        padding: 12px 14px;
        color: #D1FAE5;
        font-size: 13px;
        margin-bottom: 16px;
    }

    .stChatMessage {
        background: rgba(15,23,42,0.55);
        border-radius: 16px;
        padding: 8px;
        border: 1px solid rgba(255,255,255,0.06);
    }

    .stTextInput input {
        background-color: #0F172A !important;
        color: #E5E7EB !important;
        border-radius: 12px !important;
        border: 1px solid rgba(134,239,172,0.20) !important;
    }

    label {
        color: #E5E7EB !important;
        font-weight: 600 !important;
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: #0F172A !important;
        border-radius: 12px !important;
    }

    .stButton button {
        background: linear-gradient(90deg, #16A34A, #22C55E);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 700;
    }

    .stButton button:hover {
        border: none;
        box-shadow: 0px 8px 22px rgba(34,197,94,0.30);
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    "<div class='chat-title'>AI Customer Support Assistant</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='green-line'></div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='chat-subtitle'>Conversational banking support powered by Gemini, knowledge retrieval, and simulated banking APIs.</div>",
    unsafe_allow_html=True
)


# -----------------------------
# Session State
# -----------------------------

if "customer_id" not in st.session_state:
    st.session_state.customer_id = "CUST001"

if "agent_session" not in st.session_state:
    st.session_state.agent_session = create_session(
        customer_id=st.session_state.customer_id,
        channel="streamlit"
    )

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello, I’m your AI customer support assistant. How can I help you today?",
            "metadata": None
        }
    ]


# -----------------------------
# Top Controls
# -----------------------------

col1, col2 = st.columns([2, 1])

with col1:
    customer_id = st.selectbox(
        "Customer",
        ["CUST001", "CUST002", "CUST003"],
        index=["CUST001", "CUST002", "CUST003"].index(
            st.session_state.customer_id
        )
    )

with col2:
    reset = st.button("Reset Chat")

if customer_id != st.session_state.customer_id:
    st.session_state.customer_id = customer_id
    st.session_state.agent_session = create_session(
        customer_id=customer_id,
        channel="streamlit"
    )
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello, I’m your AI customer support assistant. How can I help you today?",
            "metadata": None
        }
    ]
    st.rerun()

if reset:
    st.session_state.agent_session = create_session(
        customer_id=st.session_state.customer_id,
        channel="streamlit"
    )
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Chat reset. How can I help you now?",
            "metadata": None
        }
    ]
    st.rerun()


st.markdown(
    f"""
    <div class='meta-box'>
        <b>Customer ID:</b> {st.session_state.customer_id}<br>
        <b>Session:</b> {st.session_state.agent_session["session_id"]}
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Demo Prompts
# -----------------------------

with st.expander("Try demo prompts"):
    st.markdown(
        """
        - My card is bad  
        - My card was stolen  
        - Yes  
        - What is my transfer limit?  
        - Someone accessed my account without permission  
        - I was debited twice yesterday  
        - Where is your Ikeja branch?
        """
    )


# -----------------------------
# Display Chat
# -----------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("metadata"):
            with st.expander("Agent details"):
                st.json(message["metadata"])


# -----------------------------
# Chat Input
# -----------------------------

user_message = st.chat_input("Type your message...")

if user_message:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
            "metadata": None
        }
    )

    with st.chat_message("user"):
        st.write(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your request..."):
            response = process_customer_message(
                customer_message=user_message,
                customer_id=st.session_state.customer_id,
                session_id=st.session_state.agent_session["session_id"]
            )

        st.write(response.customer_response)





        ticket_result = None
        escalation_result = None
        email_result = None

        should_write_ticket = response.status in {
            "resolved",
            "escalated",
            "cancelled",
            "unresolved"
        }

        if should_write_ticket:
            ticket_result = write_ticket(response)

        should_notify_team = (
            response.escalation_required
            or response.intent in {
                "double_debit",
                "wrong_beneficiary",
                "unauthorized_transaction"
            }
        )

        if should_notify_team:
            escalation_result = create_escalation(
                response=response
            )

            if escalation_result.get("success"):
                email_result = send_escalation_email(
                    escalation=escalation_result["escalation"]
                )





        metadata = {
            "ticket_id": response.ticket_id,
            "intent": response.intent,
            "sentiment": response.sentiment,
            "department": response.assigned_department,
            "priority": response.priority,
            "status": response.status,
            "escalation_required": response.escalation_required,
            "apis_called": response.api_called,
            "knowledge_sources": response.knowledge_sources,
            "created_at": response.created_at,
            "raw": response.raw,
            "ticket_result": ticket_result,
            "escalation_result": escalation_result,
            "email_result": email_result

        }

        with st.expander("Agent details"):
            st.json(metadata)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response.customer_response,
            "metadata": metadata
        }
    )