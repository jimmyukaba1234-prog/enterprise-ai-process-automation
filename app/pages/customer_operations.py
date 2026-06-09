import streamlit as st
import pandas as pd
import plotly.express as px

from app.customer_ops.sla_service import add_sla_status_to_tickets, get_sla_summary
from app.customer_ops.dispute_service import add_dispute_flags_to_tickets, get_dispute_summary

from app.customer_ops.customer_metrics import (
    get_customer_operations_metrics,
    get_department_ticket_distribution,
    get_priority_distribution,
    get_sentiment_distribution,
    get_channel_distribution,
    get_issue_category_distribution,
    get_customer_segment_distribution,
    get_repeat_customer_complaints,
    get_resolution_status_distribution,
    get_resolution_by_department,
    get_average_resolution_time_by_department,
    get_sla_met_distribution,
)

ORANGE = "#F97316"
CARD_BG = "#111827"
CARD_BG_2 = "#1E293B"
TEXT = "#FFFFFF"
MUTED = "#CBD5E1"


def style_page():
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(249,115,22,0.12), transparent 28%),
                    linear-gradient(135deg, #020617 0%, #0F172A 55%, #111827 100%);
            }

            .page-title {
                font-size: 40px;
                font-weight: 900;
                color: #FFFFFF;
                margin-bottom: 4px;
                letter-spacing: -0.6px;
            }

            .page-subtitle {
                font-size: 16px;
                color: #CBD5E1;
                margin-bottom: 28px;
            }

            .section-title {
                font-size: 22px;
                font-weight: 800;
                color: #FFFFFF;
                margin-top: 28px;
                margin-bottom: 14px;
            }

            div[data-testid="stMetric"] {
                background: linear-gradient(145deg, #111827, #1E293B);
                border: 1px solid rgba(255,255,255,0.08);
                border-left: 5px solid #F97316;
                padding: 20px;
                border-radius: 18px;
                box-shadow: 0px 8px 28px rgba(0,0,0,0.30);
            }

            div[data-testid="stMetricLabel"] {
                color: #E5E7EB !important;
                font-size: 14px !important;
                font-weight: 600 !important;
            }

            div[data-testid="stMetricValue"] {
                color: #FFFFFF !important;
                font-size: 34px !important;
                font-weight: 900 !important;
            }

            .summary-box {
                background: linear-gradient(145deg, #111827, #1E293B);
                border: 1px solid rgba(255,255,255,0.08);
                border-left: 5px solid #F97316;
                border-radius: 18px;
                padding: 22px;
                color: #E5E7EB;
                font-size: 16px;
                line-height: 1.8;
                box-shadow: 0px 8px 28px rgba(0,0,0,0.25);
                margin-top: 10px;
                margin-bottom: 22px;
            }

            .summary-box b {
                color: #F97316;
            }

            .chart-card {
                background: linear-gradient(145deg, #111827, #1E293B);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 18px;
                padding: 14px 14px 4px 14px;
                box-shadow: 0px 8px 28px rgba(0,0,0,0.25);
                margin-bottom: 18px;
            }

            .dataframe {
                color: #FFFFFF !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def load_tickets():
    try:
        return pd.read_csv("data/raw/live_tickets.csv")
    except FileNotFoundError:
        return pd.DataFrame()


def style_chart(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        font=dict(color="#E5E7EB"),
        title=dict(
            font=dict(size=16, color="#FFFFFF"),
            x=0.02
        ),
        margin=dict(l=20, r=20, t=55, b=35),
        legend=dict(
            font=dict(color="#E5E7EB"),
            bgcolor="rgba(0,0,0,0)"
        )
    )

    fig.update_xaxes(
        color="#CBD5E1",
        gridcolor="rgba(255,255,255,0.06)"
    )

    fig.update_yaxes(
        color="#CBD5E1",
        gridcolor="rgba(255,255,255,0.06)"
    )

    return fig


def render_chart_card(fig):
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_kpis(metrics, sla, disputes):
    row1 = st.columns(4)
    row1[0].metric("Total Tickets", metrics["total_tickets"])
    row1[1].metric("Open Tickets", metrics["open_tickets"])
    row1[2].metric("Escalated Tickets", metrics["escalated_tickets"])
    row1[3].metric("Dispute Cases", disputes["total_disputes"])

    row2 = st.columns(4)
    row2[0].metric("Resolved Tickets", metrics["resolved_tickets"])
    row2[1].metric("Resolution Rate", f"{metrics['resolution_rate']}%")
    row2[2].metric("Avg Resolution Time", f"{metrics['average_resolution_time']} hrs")
    row2[3].metric("Feedback Score", metrics["average_feedback_score"])

def render_empty_state():
    st.info(
        "No customer tickets found yet. Go to the Customer Chatbot tab, submit a few complaints, then return here."
    )


def render_customer_operations():
    style_page()

    st.markdown(
        "<div class='page-title'>Customer Operations Intelligence</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='page-subtitle'>AI chatbot ticketing, complaint routing, SLA monitoring, dispute detection, and customer support analytics.</div>",
        unsafe_allow_html=True
    )

    tickets_df = load_tickets()

    if tickets_df.empty:
        render_empty_state()
        return

    add_sla_status_to_tickets()
    add_dispute_flags_to_tickets()

    tickets_df = load_tickets()

    metrics = get_customer_operations_metrics()
    sla = get_sla_summary()
    disputes = get_dispute_summary()

    render_kpis(metrics, sla, disputes)

    st.markdown(
        f"""
        <div class='summary-box'>
            <b>AI Operations Summary:</b><br>
            The customer operations layer is currently tracking <b>{metrics['total_tickets']}</b> tickets,
            including <b>{metrics['escalated_tickets']}</b> escalated cases and
            <b>{disputes['total_disputes']}</b> dispute-related cases. SLA monitoring shows
            <b>{sla['breached']}</b> breached tickets and
            <b>{sla['approaching_breach']}</b> tickets approaching breach. This gives support teams
            a real-time view of workload, risk, and customer urgency.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='section-title'>Operational Analytics</div>", unsafe_allow_html=True)

    department_df = get_department_ticket_distribution()
    priority_df = get_priority_distribution()

    sla_df = pd.DataFrame({
        "SLA Status": ["Within SLA", "Approaching Breach", "Breached"],
        "Count": [
            sla["within_sla"],
            sla["approaching_breach"],
            sla["breached"]
        ]
    })

    col1, col2, col3 = st.columns(3)

    with col1:
        if not department_df.empty:
            fig = px.bar(
                department_df,
                x="assigned_department",
                y="ticket_count",
                title="Tickets by Department",
                text="ticket_count",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No department data available.")

    with col2:
        if not priority_df.empty:
            fig = px.pie(
                priority_df,
                names="priority",
                values="ticket_count",
                title="Tickets by Priority",
                hole=0.55,
                color_discrete_sequence=[
                    "#EF4444",
                    "#F97316",
                    "#FBBF24",
                    "#22C55E"
                ]
            )
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No priority data available.")

    with col3:
        fig = px.pie(
            sla_df,
            names="SLA Status",
            values="Count",
            title="SLA Status Overview",
            hole=0.55,
            color="SLA Status",
            color_discrete_map={
                "Within SLA": "#22C55E",
                "Approaching Breach": "#F59E0B",
                "Breached": "#EF4444"
            }
        )
        render_chart_card(style_chart(fig, 345))






    st.markdown("<div class='section-title'>Customer Risk & Escalation Intelligence</div>", unsafe_allow_html=True)

    sentiment_df = get_sentiment_distribution()

    dispute_count = disputes["total_disputes"]
    non_dispute_count = max(metrics["total_tickets"] - dispute_count, 0)

    dispute_df = pd.DataFrame({
        "Case Type": ["Dispute", "Non-Dispute"],
        "Count": [dispute_count, non_dispute_count]
    })

    if "email_sent" in tickets_df.columns:
        email_df = (
            tickets_df["email_sent"]
            .astype(str)
            .replace({"True": "Email Sent", "False": "Dashboard Only", "true": "Email Sent", "false": "Dashboard Only"})
            .value_counts()
            .reset_index()
        )
        email_df.columns = ["Notification Status", "Count"]
    else:
        email_df = pd.DataFrame(columns=["Notification Status", "Count"])

    col4, col5, col6 = st.columns(3)

    with col4:
        if not sentiment_df.empty:
            fig = px.bar(
                sentiment_df,
                x="sentiment",
                y="ticket_count",
                title="Customer Sentiment",
                text="ticket_count",
                color="sentiment",
                color_discrete_map={
                    "Positive": "#22C55E",
                    "Neutral": "#F59E0B",
                    "Negative": "#EF4444"
                }
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No sentiment data available.")

    with col5:
        fig = px.pie(
            dispute_df,
            names="Case Type",
            values="Count",
            title="Dispute vs Non-Dispute",
            hole=0.55,
            color_discrete_sequence=["#F97316", "#334155"]
        )
        render_chart_card(style_chart(fig, 345))

    with col6:
        if not email_df.empty:
            fig = px.pie(
                email_df,
                names="Notification Status",
                values="Count",
                title="Email Escalation Status",
                hole=0.55,
                color_discrete_sequence=["#22C55E", "#64748B"]
            )
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No notification data available.")




    st.markdown("<div class='section-title'>Customer Lifecycle Intelligence</div>", unsafe_allow_html=True)

    channel_df = get_channel_distribution()
    segment_df = get_customer_segment_distribution()

    onboarding_df = pd.DataFrame({
        "Stage": ["Lead", "Signup", "KYC Submitted", "KYC Approved", "Active Customer"],
        "Count": [120, 96, 72, 58, 49]
    })

    lifecycle_col1, lifecycle_col2, lifecycle_col3 = st.columns(3)

    with lifecycle_col1:
        if not channel_df.empty:
            fig = px.bar(
                channel_df,
                x="channel",
                y="ticket_count",
                title="Complaint Channels",
                text="ticket_count",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig, 345))

    with lifecycle_col2:
        if not segment_df.empty:
            fig = px.pie(
                segment_df,
                names="customer_segment",
                values="ticket_count",
                title="Customer Segment Distribution",
                hole=0.55,
                color_discrete_sequence=["#F97316", "#FDBA74", "#64748B"]
            )
            render_chart_card(style_chart(fig, 345))

    with lifecycle_col3:
        fig = px.funnel(
            onboarding_df,
            x="Count",
            y="Stage",
            title="Customer Onboarding Funnel",
            color_discrete_sequence=[ORANGE]
        )
        render_chart_card(style_chart(fig, 345))

    st.markdown(
        """
        <div class='summary-box'>
            <b>Production Flow:</b><br>
            In this demo, customer lifecycle analytics are partly simulated and partly powered by chatbot ticket data.
            In production, this layer would connect to the bank app, web onboarding forms, CRM, KYC provider,
            core banking customer records, and lead management tools through APIs, webhooks, and database sync.
            When customers sign up, submit KYC, become active, or raise issues, those events update the dashboard automatically.
        </div>
        """,
        unsafe_allow_html=True
    )






    st.markdown("<div class='section-title'>Customer Activity & Transaction Monitoring</div>", unsafe_allow_html=True)

    issue_category_df = get_issue_category_distribution()
    repeat_customers_df = get_repeat_customer_complaints()

    if "intent" in tickets_df.columns:
        transaction_issue_df = (
            tickets_df[
                tickets_df["intent"].isin([
                    "failed_transaction",
                    "double_debit",
                    "fraud_alert",
                    "card_issue"
                ])
            ]
            .groupby("intent")
            .size()
            .reset_index(name="ticket_count")
        )
    else:
        transaction_issue_df = pd.DataFrame()

    activity_col1, activity_col2, activity_col3 = st.columns(3)

    with activity_col1:
        if not issue_category_df.empty:
            fig = px.bar(
                issue_category_df,
                x="issue_category",
                y="ticket_count",
                title="Issue Category Breakdown",
                text="ticket_count",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No issue category data available.")

    with activity_col2:
        if not transaction_issue_df.empty:
            fig = px.pie(
                transaction_issue_df,
                names="intent",
                values="ticket_count",
                title="Transaction & Risk Issue Breakdown",
                hole=0.55,
                color_discrete_sequence=[
                    "#EF4444",
                    "#F97316",
                    "#F59E0B",
                    "#64748B"
                ]
            )
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No transaction issue data available.")

    with activity_col3:
        if not repeat_customers_df.empty:
            fig = px.bar(
                repeat_customers_df,
                x="customer_id",
                y="complaint_count",
                title="Repeat Customer Complaints",
                text="complaint_count",
                color_discrete_sequence=["#FDBA74"]
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No repeat complaint data available.")

    st.markdown(
        """
        <div class='summary-box'>
            <b>Production Flow:</b><br>
            In this demo, transaction and activity monitoring is derived from chatbot ticket intents such as 
            failed transactions, double debits, fraud alerts, card issues, KYC issues, and technical complaints.
            In production, this would connect to transaction APIs, customer activity logs, CRM records,
            fraud monitoring systems, support ticketing tools, and core banking event streams. 
            The system can detect customer footprints, repeated complaints, transaction issues, fraud signals,
            and unresolved customer journeys automatically.
        </div>
        """,
        unsafe_allow_html=True
    )





    st.markdown("<div class='section-title'>Resolution & SLA Performance</div>", unsafe_allow_html=True)

    resolution_status_df = get_resolution_status_distribution()
    resolution_department_df = get_resolution_by_department()
    resolution_time_df = get_average_resolution_time_by_department()
    sla_met_df = get_sla_met_distribution()

    resolution_col1, resolution_col2, resolution_col3 = st.columns(3)

    with resolution_col1:
        if not resolution_status_df.empty:
            fig = px.pie(
                resolution_status_df,
                names="resolution_status",
                values="ticket_count",
                title="Resolution Status Distribution",
                hole=0.55,
                color="resolution_status",
                color_discrete_map={
                    "Resolved": "#22C55E",
                    "Escalated": "#EF4444",
                    "Open": "#F59E0B",
                    "In Progress": "#64748B"
                }
            )
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No resolution data available.")

    with resolution_col2:
        if not resolution_time_df.empty:
            fig = px.bar(
                resolution_time_df,
                x="assigned_department",
                y="avg_resolution_hours",
                title="Average Resolution Time by Department",
                text="avg_resolution_hours",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No resolution time data available.")

    with resolution_col3:
        if not sla_met_df.empty:
            fig = px.pie(
                sla_met_df,
                names="sla_met",
                values="ticket_count",
                title="SLA Met vs Breached",
                hole=0.55,
                color_discrete_sequence=[
                    "#22C55E",
                    "#EF4444",
                    "#64748B"
                ]
            )
            render_chart_card(style_chart(fig, 345))
        else:
            st.info("No SLA resolution data available.")

    st.markdown(
        f"""
        <div class='summary-box'>
            <b>Resolution Intelligence:</b><br>
            The system currently tracks simulated ticket resolution workflows, SLA compliance,
            escalation handling, and customer feedback scoring. Resolution analytics currently show
            a <b>{metrics['resolution_rate']}%</b> resolution rate with an average resolution time of
            <b>{metrics['average_resolution_time']} hours</b>.

            In production, support teams, CRM platforms, dispute management systems,
            and customer support tools would update ticket status automatically through APIs,
            webhooks, workflow engines, and database synchronization whenever a customer issue is resolved.
            This enables real-time SLA tracking, dispute closure monitoring,
            customer satisfaction analytics, and operational performance reporting.
        </div>
        """,
        unsafe_allow_html=True
    )






    st.markdown("<div class='section-title'>Recent Customer Tickets</div>", unsafe_allow_html=True)

    display_columns = [
        "ticket_id",
        "customer_id",
        "intent",
        "assigned_department",
        "priority",
        "status",
        "sla_status",
        "is_dispute",
        "created_at",
        "sla_deadline",
        "email_sent"
    ]

    available_columns = [
        col for col in display_columns
        if col in tickets_df.columns
    ]

    st.dataframe(
        tickets_df[available_columns].tail(25),
        use_container_width=True,
        height=420
    )