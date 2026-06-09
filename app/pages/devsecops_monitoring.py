import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.devsecops.log_generator import generate_logs
from app.devsecops.log_analyzer import analyze_logs
from app.devsecops.incident_summarizer import generate_incident_summaries
from app.devsecops.alert_engine import generate_alerts
from app.devsecops.devsecops_metrics import (
    get_devsecops_metrics,
    get_logs_by_service,
    get_alert_summary,
    get_event_type_distribution,
    get_severity_distribution,
    get_incident_type_distribution,
    get_escalation_distribution,
)


ORANGE = "#F97316"


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
        </style>
        """,
        unsafe_allow_html=True
    )


def style_chart(fig, height=350):
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


def render_chart_card(fig):
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def run_devsecops_pipeline():
    generate_logs(40)
    analyze_logs()
    generate_incident_summaries()
    generate_alerts()


def load_logs():
    try:
        return pd.read_csv("data/raw/system_logs.csv")
    except FileNotFoundError:
        return pd.DataFrame()


def render_devsecops_monitoring():
    style_page()

    st.markdown(
        "<div class='page-title'>DevSecOps Intelligence Command Center</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='page-subtitle'>Repository automation, CI/CD pipeline monitoring, system health checks, incident detection, alert escalation, and AI-assisted operational summaries.</div>",
        unsafe_allow_html=True
    )

    if st.button("Run DevSecOps Monitoring Pipeline"):
        run_devsecops_pipeline()
        st.success("DevSecOps monitoring pipeline executed successfully. Critical alerts will trigger escalation emails.")

    metrics = get_devsecops_metrics()
    logs_df = load_logs()
    alerts_df = get_alert_summary()

    row1 = st.columns(4)
    row1[0].metric("Total Logs", metrics["total_logs"])
    row1[1].metric("Total Incidents", metrics["total_incidents"])
    row1[2].metric("Critical Alerts", metrics["critical_alerts"])
    row1[3].metric("Escalated Alerts", metrics["escalated_alerts"])

    row2 = st.columns(4)
    row2[0].metric("Pipeline Events", metrics["pipeline_events"])
    row2[1].metric("Repository Events", metrics["repository_events"])
    row2[2].metric("System Checks", metrics["system_check_events"])
    row2[3].metric("Total Alerts", metrics["total_alerts"])

    st.markdown(
        f"""
        <div class='summary-box'>
            <b>AI DevSecOps Summary:</b><br>
            The monitoring layer has processed <b>{metrics['total_logs']}</b> technical events,
            including <b>{metrics['pipeline_events']}</b> pipeline events,
            <b>{metrics['repository_events']}</b> repository automation events, and
            <b>{metrics['system_check_events']}</b> system check events. 
            The system detected <b>{metrics['total_incidents']}</b> incidents and generated
            <b>{metrics['total_alerts']}</b> alerts, with <b>{metrics['escalated_alerts']}</b> already escalated.
        </div>
        """,
        unsafe_allow_html=True
    )






    st.markdown(
        "<div class='section-title'>Operations Monitoring</div>",
        unsafe_allow_html=True
    )

    logs_by_service = get_logs_by_service()
    severity_df = get_severity_distribution()
    incident_type_df = get_incident_type_distribution()

    ops_col1, ops_col2, ops_col3 = st.columns(3)

    with ops_col1:
        if not logs_by_service.empty:
            fig = px.bar(
                logs_by_service,
                x="service_name",
                y="log_count",
                title="Logs by Service",
                text="log_count",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig))
        else:
            st.info("No logs available yet.")

    with ops_col2:
        if not severity_df.empty:
            fig = px.pie(
                severity_df,
                names="severity",
                values="severity_count",
                title="Severity Distribution",
                hole=0.55,
                color="severity",
                color_discrete_map={
                    "Info": "#22C55E",
                    "Warning": "#F59E0B",
                    "Error": "#F97316",
                    "Critical": "#EF4444"
                }
            )
            render_chart_card(style_chart(fig))
        else:
            st.info("No severity data available.")

    with ops_col3:
        if not incident_type_df.empty:
            fig = px.bar(
                incident_type_df,
                x="incident_count",
                y="incident_type",
                title="Incident Type Distribution",
                text="incident_count",
                orientation="h",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig))
        else:
            st.info("No incident type data available.")





    

    st.markdown(
        "<div class='section-title'>Repository & Pipeline Automation</div>",
        unsafe_allow_html=True
    )

    event_type_df = get_event_type_distribution()

    pipeline_status_df = pd.DataFrame({
        "Pipeline Status": [
            "Build Triggered",
            "Tests Passed",
            "Deployment Successful",
            "Pipeline Failed",
            "Rollback Initiated"
        ],
        "Count": [
            18,
            14,
            11,
            4,
            2
        ]
    })

    repository_status_df = pd.DataFrame({
        "Repository Event": [
            "Pull Requests",
            "Code Reviews",
            "Merge Conflicts",
            "Review Changes",
            "Merged Successfully"
        ],
        "Count": [
            22,
            17,
            5,
            7,
            14
        ]
    })

    st.markdown(
        """
        <div class='summary-box'>
            <b>Production Flow:</b><br>
            In production, repository and pipeline events would be ingested through GitHub APIs, 
            GitHub Actions webhooks, CI/CD pipeline APIs, and deployment tool webhooks. 
            When a pull request is created, code is reviewed, tests run, or deployments succeed/fail, 
            those events are sent as JSON payloads into this platform for monitoring, automation, analytics, 
            and escalation.
        </div>
        """,
        unsafe_allow_html=True
    )

    repo_col1, repo_col2, repo_col3 = st.columns(3)

    with repo_col1:
        if not event_type_df.empty:
            fig = px.pie(
                event_type_df,
                names="event_type",
                values="event_count",
                title="Event Type Distribution",
                hole=0.55,
                color_discrete_sequence=[
                    "#F97316",
                    "#FDBA74",
                    "#FBBF24"
                ]
            )
            render_chart_card(style_chart(fig))
        else:
            st.info("No event type data available.")

    with repo_col2:
        fig = px.bar(
            pipeline_status_df,
            x="Pipeline Status",
            y="Count",
            title="CI/CD Pipeline Automation",
            text="Count",
            color_discrete_sequence=[ORANGE]
        )
        fig.update_traces(textposition="outside")
        render_chart_card(style_chart(fig))

    with repo_col3:
        fig = px.bar(
            repository_status_df,
            x="Repository Event",
            y="Count",
            title="Repository Automation",
            text="Count",
            color_discrete_sequence=["#FDBA74"]
        )
        fig.update_traces(textposition="outside")
        render_chart_card(style_chart(fig))












    st.markdown(
        "<div class='section-title'>Security & Risk Monitoring</div>",
        unsafe_allow_html=True
    )

    security_df = pd.DataFrame({
        "Security Check": [
            "Failed Authentication",
            "Vulnerability Findings",
            "Hardening Checks",
            "Access Risks",
            "Suspicious Requests"
        ],
        "Count": [
            int(logs_df["message"].astype(str).str.lower().str.contains("failed authentication").sum()) if not logs_df.empty else 0,
            int(logs_df["message"].astype(str).str.lower().str.contains("vulnerability").sum()) if not logs_df.empty else 0,
            12,
            5,
            int(logs_df["message"].astype(str).str.lower().str.contains("unusual request").sum()) if not logs_df.empty else 0
        ]
    })

    scan_status_df = pd.DataFrame({
        "Scan Type": [
            "Vulnerability Scan",
            "Penetration Test",
            "Dependency Scan",
            "Container Scan",
            "Cloud Config Scan"
        ],
        "Status Count": [
            14,
            6,
            11,
            8,
            9
        ]
    })

    st.markdown(
        """
        <div class='summary-box'>
            <b>Production Flow:</b><br>
            In production, this layer connects to security scanners and monitoring tools such as 
            Snyk, SonarQube, GitHub Dependabot, OWASP ZAP, cloud security tools, SIEM platforms, 
            and vulnerability scanners. These tools can send scan results through APIs or webhooks, 
            allowing the platform to detect risks, summarize vulnerabilities, and escalate critical findings.
        </div>
        """,
        unsafe_allow_html=True
    )

    sec_col1, sec_col2, sec_col3 = st.columns(3)

    with sec_col1:
        fig = px.bar(
            security_df,
            x="Security Check",
            y="Count",
            title="Security & Access Risk Signals",
            text="Count",
            color_discrete_sequence=[ORANGE]
        )
        fig.update_traces(textposition="outside")
        render_chart_card(style_chart(fig))

    with sec_col2:
        fig = px.pie(
            scan_status_df,
            names="Scan Type",
            values="Status Count",
            title="Security Scan Coverage",
            hole=0.55,
            color_discrete_sequence=[
                "#F97316",
                "#FDBA74",
                "#FBBF24",
                "#EF4444",
                "#22C55E"
            ]
        )
        render_chart_card(style_chart(fig))

    with sec_col3:
        risk_score = min(
            100,
            metrics["critical_logs"] * 10 + metrics["error_logs"] * 4
        )

        gauge_fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=risk_score,
                number={"suffix": "%", "font": {"color": "#FFFFFF", "size": 38}},
                title={"text": "Security Risk Score", "font": {"color": "#FFFFFF", "size": 16}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#CBD5E1"},
                    "bar": {"color": "#EF4444" if risk_score > 60 else ORANGE},
                    "bgcolor": "#1E293B",
                    "borderwidth": 1,
                    "bordercolor": "rgba(255,255,255,0.1)"
                }
            )
        )

        gauge_fig.update_layout(
            height=350,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#E5E7EB"),
            margin=dict(l=20, r=20, t=60, b=20)
        )

        render_chart_card(gauge_fig)







    st.markdown(
        "<div class='section-title'>Escalation Intelligence</div>",
        unsafe_allow_html=True
    )

    escalation_df = get_escalation_distribution()

    if not alerts_df.empty and "alert_level" in alerts_df.columns:
        alert_level_df = (
            alerts_df.groupby("alert_level")
            .size()
            .reset_index(name="alert_count")
        )
    else:
        alert_level_df = pd.DataFrame()

    if not alerts_df.empty and "escalation_status" in alerts_df.columns:
        escalation_status_df = (
            alerts_df.groupby("escalation_status")
            .size()
            .reset_index(name="alert_count")
        )
    else:
        escalation_status_df = pd.DataFrame()

    esc_col1, esc_col2, esc_col3 = st.columns(3)

    with esc_col1:
        if not alert_level_df.empty:
            fig = px.pie(
                alert_level_df,
                names="alert_level",
                values="alert_count",
                title="Alert Level Distribution",
                hole=0.55,
                color_discrete_sequence=[
                    "#EF4444",
                    "#F97316",
                    "#FBBF24",
                    "#64748B"
                ]
            )
            render_chart_card(style_chart(fig))
        else:
            st.info("No alert level data available.")

    with esc_col2:
        if not escalation_df.empty:
            fig = px.bar(
                escalation_df,
                x="escalation_channel",
                y="alert_count",
                title="Escalation Channel Distribution",
                text="alert_count",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig))
        else:
            st.info("No escalation channel data available.")

    with esc_col3:
        if not escalation_status_df.empty:
            fig = px.pie(
                escalation_status_df,
                names="escalation_status",
                values="alert_count",
                title="Escalation Status",
                hole=0.55,
                color_discrete_sequence=[
                    "#22C55E",
                    "#F97316",
                    "#EF4444",
                    "#64748B"
                ]
            )
            render_chart_card(style_chart(fig))
        else:
            st.info("No escalation status data available.")

    st.markdown(
        """
        <div class='summary-box'>
            <b>Escalation Flow:</b><br>
            Critical logs are converted into Critical Alerts and automatically escalated by email.
            High alerts are routed to email, while medium alerts remain visible on the dashboard.
            In production, escalation can be extended to Microsoft Teams, Slack, PagerDuty, Opsgenie,
            Jira, ServiceNow, SMS, or WhatsApp depending on incident severity.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Recent System Logs</div>",
        unsafe_allow_html=True
    )

    if logs_df.empty:
        st.info("No system logs available.")
    else:
        display_cols = [
            "log_id",
            "event_type",
            "service_name",
            "severity",
            "message",
            "is_incident",
            "incident_type",
            "incident_summary",
            "created_at"
        ]

        available_cols = [
            col for col in display_cols
            if col in logs_df.columns
        ]

        st.dataframe(
            logs_df[available_cols].tail(25),
            use_container_width=True,
            height=420
        )

    st.markdown(
        "<div class='section-title'>Generated Alerts & Escalations</div>",
        unsafe_allow_html=True
    )

    if alerts_df.empty:
        st.info("No generated alerts yet.")
    else:
        alert_cols = [
            "log_id",
            "event_type",
            "service_name",
            "severity",
            "alert_level",
            "escalation_required",
            "escalation_channel",
            "escalation_status",
            "message",
            "created_at"
        ]

        available_alert_cols = [
            col for col in alert_cols
            if col in alerts_df.columns
        ]

        st.dataframe(
            alerts_df[available_alert_cols].tail(25),
            use_container_width=True,
            height=420
        )



