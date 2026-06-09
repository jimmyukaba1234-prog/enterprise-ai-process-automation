import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.hr.cv_intake import load_received_applications

from app.customer_ops.customer_metrics import (
    get_customer_operations_metrics,
    get_department_ticket_distribution,
    get_priority_distribution,
    get_issue_category_distribution,
    get_resolution_status_distribution,
)

from app.customer_ops.sla_service import get_sla_summary
from app.customer_ops.dispute_service import get_dispute_summary

from app.hr.hr_metrics import get_hr_metrics

from app.devsecops.devsecops_metrics import (
    get_devsecops_metrics,
    get_alert_summary,
    get_event_type_distribution,
    get_escalation_distribution
)


ORANGE = "#F97316"


def style_page():
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(135deg, #020617 0%, #0F172A 55%, #111827 100%);
            }

            .page-title {
                font-size: 40px;
                font-weight: 900;
                color: #FFFFFF;
                margin-bottom: 4px;
                letter-spacing: -0.5px;
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
                margin-top: 24px;
                margin-bottom: 12px;
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
                padding: 24px;
                color: #E5E7EB;
                font-size: 16px;
                line-height: 1.8;
                box-shadow: 0px 8px 28px rgba(0,0,0,0.25);
            }

            .summary-box b {
                color: #F97316;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_gauge(title: str, value: float, label: str):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%", "font": {"color": "#FFFFFF", "size": 34}},
            title={"text": title, "font": {"color": "#FFFFFF", "size": 18}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#CBD5E1"},
                "bar": {"color": ORANGE},
                "bgcolor": "#1E293B",
                "borderwidth": 1,
                "bordercolor": "rgba(255,255,255,0.15)",
            }
        )
    )

    fig.update_layout(
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=55, b=20),
        annotations=[
            dict(
                text=label,
                x=0.5,
                y=0.02,
                showarrow=False,
                font=dict(size=14, color="#22C55E")
            )
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

def style_chart(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        font=dict(color="#E5E7EB"),
        title=dict(font=dict(size=16, color="#FFFFFF"), x=0.02),
        margin=dict(l=20, r=20, t=55, b=35),
        legend=dict(font=dict(color="#E5E7EB"), bgcolor="rgba(0,0,0,0)")
    )

    fig.update_xaxes(color="#CBD5E1", gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(color="#CBD5E1", gridcolor="rgba(255,255,255,0.06)")

    return fig



def render_executive_dashboard():
    style_page()

    st.markdown("<div class='page-title'>Executive AI Operations Command Center</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>A centralized intelligence view across customer operations, HR automation, and DevSecOps monitoring.</div>",
        unsafe_allow_html=True
    )

    customer = get_customer_operations_metrics()
    sla = get_sla_summary()
    disputes = get_dispute_summary()
    hr = get_hr_metrics()
    devsecops = get_devsecops_metrics()

    row1 = st.columns(4)
    row1[0].metric("Customer Tickets", customer["total_tickets"])
    row1[1].metric("Resolution Rate", f"{customer['resolution_rate']}%")
    row1[2].metric("HR Candidates", hr["total_candidates"])
    #row1[3].metric("System Incidents", devsecops["total_incidents"])
    row1[3].metric("System Health", f"{max(0, 100 - devsecops['total_incidents'])}%")

    row2 = st.columns(4)
    row2[0].metric("Dispute Cases", disputes["total_disputes"])
    row2[1].metric("Pending Onboarding", hr["pending_onboarding"])
    row2[2].metric("Critical Alerts", devsecops["critical_alerts"])
    row2[3].metric("Escalated Alerts", devsecops["escalated_alerts"])


    total_sla = sla["total_tickets"]
    sla_health = round((sla["within_sla"] / total_sla) * 100, 2) if total_sla else 0

    resolution_health = customer["resolution_rate"]
    system_health = max(0, 100 - devsecops["total_incidents"])

    st.markdown("<div class='section-title'>Executive Health Indicators</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        render_gauge("Customer SLA Health", sla_health, "Within SLA")

    with col2:
        render_gauge("Resolution Health", resolution_health, "Resolved Cases")

    with col3:
        render_gauge("System Health Score", system_health, "Operational Health")

    st.markdown("<div class='section-title'>AI Executive Summary</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='summary-box'>
        <b>AI Executive Summary:</b><br>
        The platform is monitoring <b>{customer['total_tickets']}</b> customer tickets with 
        a <b>{customer['resolution_rate']}%</b> resolution rate and 
        <b>{disputes['total_disputes']}</b> dispute cases. HR has processed 
        <b>{hr['total_candidates']}</b> candidates with <b>{hr['pending_onboarding']}</b> pending onboarding tasks. 
        DevSecOps has detected <b>{devsecops['total_incidents']}</b> incidents, 
        <b>{devsecops['critical_alerts']}</b> critical alerts, and 
        <b>{devsecops['escalated_alerts']}</b> escalated alerts.
        </div>
        """,
        unsafe_allow_html=True
    )
   



    st.markdown("<div class='section-title'>Cross-Department Intelligence</div>", unsafe_allow_html=True)

    dept_df = get_department_ticket_distribution()
    issue_category_df = get_issue_category_distribution()
    alerts_df = get_alert_summary()
    event_type_df = get_event_type_distribution()

    col4, col5, col6 = st.columns(3)

    with col4:
        if not dept_df.empty:
            fig = px.bar(
                dept_df,
                x="assigned_department",
                y="ticket_count",
                title="Customer Tickets by Department",
                text="ticket_count",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with col5:
        if not issue_category_df.empty:
            fig = px.pie(
                issue_category_df,
                names="issue_category",
                values="ticket_count",
                title="Customer Issue Categories",
                hole=0.55,
                color_discrete_sequence=["#F97316", "#FDBA74", "#FBBF24", "#EF4444", "#22C55E"]
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with col6:
        if not alerts_df.empty:
            alert_counts = (
                alerts_df.groupby("alert_level")
                .size()
                .reset_index(name="alert_count")
            )

            fig = px.pie(
                alert_counts,
                names="alert_level",
                values="alert_count",
                title="DevSecOps Alerts by Severity",
                hole=0.55,
                color_discrete_sequence=["#EF4444", "#F97316", "#FBBF24", "#22C55E"]
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)




    st.markdown("<div class='section-title'>Performance & Risk Intelligence</div>", unsafe_allow_html=True)

    resolution_df = get_resolution_status_distribution()

    hr_funnel_df = pd.DataFrame({
        "stage": [
            "Applications",
            "Shortlisted",
            "Interview Scheduled",
            "Hired"
        ],
        "count": [
            hr["total_candidates"],
            hr["shortlisted_candidates"],
            hr["interviews_scheduled"],
            hr["hired_candidates"]
        ]
    })

    col7, col8, col9 = st.columns(3)

    with col7:
        if not resolution_df.empty:
            fig = px.pie(
                resolution_df,
                names="resolution_status",
                values="ticket_count",
                title="Customer Resolution Status",
                hole=0.55,
                color_discrete_sequence=["#22C55E", "#F97316", "#EF4444", "#64748B"]
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with col8:
        fig = px.funnel(
            hr_funnel_df,
            x="count",
            y="stage",
            title="HR Recruitment Funnel",
            color_discrete_sequence=[ORANGE]
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)

    with col9:
        if not event_type_df.empty:
            fig = px.pie(
                event_type_df,
                names="event_type",
                values="event_count",
                title="DevSecOps Event Type Distribution",
                hole=0.55,
                color_discrete_sequence=["#F97316", "#FDBA74", "#FBBF24"]
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)






    st.markdown("<div class='section-title'>Department Performance Breakdown</div>", unsafe_allow_html=True)

    candidates_df = load_received_applications()
    priority_df = get_priority_distribution()

    if not candidates_df.empty and "status" in candidates_df.columns:
        candidate_status_df = (
            candidates_df.groupby("status")
            .size()
            .reset_index(name="candidate_count")
        )
    else:
        candidate_status_df = pd.DataFrame()

    escalation_df = get_escalation_distribution()

    col10, col11, col12 = st.columns(3)

    with col10:
        if not candidate_status_df.empty:
            fig = px.pie(
                candidate_status_df,
                names="status",
                values="candidate_count",
                title="HR Candidate Status Distribution",
                hole=0.55,
                color_discrete_sequence=[
                    "#F97316",
                    "#FDBA74",
                    "#FBBF24",
                    "#22C55E",
                    "#EF4444",
                    "#64748B"
                ]
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with col11:
        if not escalation_df.empty:
            fig = px.bar(
                escalation_df,
                x="escalation_channel",
                y="alert_count",
                title="DevSecOps Escalation Channels",
                text="alert_count",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with col12:
        if not priority_df.empty:
            fig = px.pie(
                priority_df,
                names="priority",
                values="ticket_count",
                title="Customer Ticket Priority",
                hole=0.55,
                color_discrete_sequence=[
                    "#EF4444",
                    "#F97316",
                    "#FBBF24",
                    "#22C55E"
                ]
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)





    st.markdown("<div class='section-title'>Enterprise AI Operations Overview</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='summary-box'>
        <b>Enterprise Production Architecture:</b><br><br>

        The current demo simulates a centralized enterprise AI operations platform integrating
        Customer Operations, HR Automation, and DevSecOps monitoring into a unified intelligence layer.

        <br><br>

        <b>Customer Operations:</b><br>
        AI chatbots, ticket routing, dispute monitoring, SLA tracking, CRM intelligence,
        customer footprint monitoring, and transaction issue detection are currently powered
        through simulated chatbot workflows and operational analytics.

        In production, this layer would integrate with:
        core banking systems, CRM platforms, mobile banking applications,
        support ticketing systems, fraud engines, KYC providers, and customer activity APIs.

        <br><br>

        <b>HR Automation:</b><br>
        Recruitment analytics, onboarding intelligence, candidate screening,
        and workforce monitoring are currently simulated using generated HR workflow data.

        In production, this layer would connect to:
        ATS platforms, LinkedIn APIs, HRIS systems, onboarding portals,
        payroll systems, document verification tools, and employee workflow engines.

        <br><br>

        <b>DevSecOps Monitoring:</b><br>
        The platform currently simulates infrastructure monitoring, operational risk detection,
        alert escalation, and incident intelligence using generated technical logs.

        In production, this would integrate with:
        GitHub APIs, GitHub Actions, CI/CD pipelines, Kubernetes,
        cloud monitoring tools, SIEM/security scanners,
        vulnerability scanners, observability platforms, and webhook-based alerting systems.

        <br><br>

        <b>Current Executive Health:</b><br>
        The organization currently maintains a
        <b>{customer['resolution_rate']}%</b> customer resolution rate while monitoring
        <b>{devsecops['total_incidents']}</b> operational incidents,
        <b>{devsecops['critical_alerts']}</b> critical alerts,
        and <b>{hr['pending_onboarding']}</b> pending onboarding workflows.
        </div>
        """,
        unsafe_allow_html=True
    )
