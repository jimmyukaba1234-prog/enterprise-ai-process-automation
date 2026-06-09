import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.hr.cv_intake import get_cv_intake_summary, load_received_applications
from app.hr.cv_ranker import rank_candidates
from app.hr.onboarding_tracker import get_onboarding_summary, get_pending_tasks
from app.hr.hr_metrics import get_hr_metrics
from app.hr.jd_generator import generate_job_description


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


def render_hr_automation():
    style_page()

    st.markdown(
        "<div class='page-title'>HR Automation Intelligence Center</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='page-subtitle'>AI-powered recruitment, job description generation, candidate ranking, interview pipeline tracking and onboarding intelligence.</div>",
        unsafe_allow_html=True
    )

    candidates_df = load_received_applications()

    if candidates_df.empty:
        st.info("No HR candidate data found. Please generate synthetic HR data first.")
        return

    metrics = get_hr_metrics()
    intake = get_cv_intake_summary()
    onboarding = get_onboarding_summary()

    offers_sent = metrics["hired_candidates"] + metrics["shortlisted_candidates"]
    offers_accepted = metrics["hired_candidates"]

    if offers_sent > 0:
        offer_acceptance_rate = round((offers_accepted / offers_sent) * 100, 1)
    else:
        offer_acceptance_rate = 0

    row1 = st.columns(4)
    row1[0].metric("Total Applications", intake["total_applications"])
    row1[1].metric("Shortlisted", metrics["shortlisted_candidates"])
    row1[2].metric("Interviews Scheduled", metrics["interviews_scheduled"])
    row1[3].metric("Hired Candidates", metrics["hired_candidates"])

    row2 = st.columns(4)
    row2[0].metric("Offers Sent", offers_sent)
    row2[1].metric("Offer Acceptance", f"{offer_acceptance_rate}%")
    row2[2].metric("Pending Onboarding", metrics["pending_onboarding"])
    row2[3].metric("Completed Onboarding", onboarding.get("completed", 0))

    st.markdown(
        f"""
        <div class='summary-box'>
            <b>AI HR Summary:</b><br>
            The HR automation layer has received <b>{intake['total_applications']}</b> applications across 
            <b>{intake['roles_receiving_applications']}</b> active roles. The AI screening workflow has identified 
            <b>{metrics['shortlisted_candidates']}</b> shortlisted candidates, scheduled 
            <b>{metrics['interviews_scheduled']}</b> interviews, and completed onboarding for 
            <b>{onboarding.get('completed', 0)}</b> new employees.
        </div>
        """,
        unsafe_allow_html=True
    )

    def style_chart(fig, height=350):
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


    st.markdown(
        "<div class='section-title'>Recruitment Intelligence</div>",
        unsafe_allow_html=True
    )

    role_counts = (
        candidates_df.groupby("role_applied")
        .size()
        .reset_index(name="candidate_count")
        .sort_values(by="candidate_count", ascending=False)
    )

    status_counts = (
        candidates_df.groupby("status")
        .size()
        .reset_index(name="candidate_count")
    )

    funnel_df = pd.DataFrame({
        "stage": [
            "Applications",
            "Shortlisted",
            "Interview Scheduled",
            "Hired"
        ],
        "count": [
            metrics["total_candidates"],
            metrics["shortlisted_candidates"],
            metrics["interviews_scheduled"],
            metrics["hired_candidates"]
        ]
    })

    col1, col2, col3 = st.columns(3)

    with col1:
        fig = px.bar(
            role_counts,
            x="role_applied",
            y="candidate_count",
            title="Applications by Role",
            text="candidate_count",
            color_discrete_sequence=[ORANGE]
        )
        fig.update_traces(textposition="outside")
        render_chart_card(style_chart(fig))

    with col2:
        fig = px.pie(
            status_counts,
            names="status",
            values="candidate_count",
            title="Candidate Status Distribution",
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
        render_chart_card(style_chart(fig))

    with col3:
        fig = px.funnel(
            funnel_df,
            x="count",
            y="stage",
            title="Recruitment Pipeline Funnel",
            color_discrete_sequence=[ORANGE]
        )
        render_chart_card(style_chart(fig))








    st.markdown(
        "<div class='section-title'>Candidate Intelligence</div>",
        unsafe_allow_html=True
    )

    candidate_df = candidates_df.copy()

    if "skills_match_score" in candidate_df.columns:
        ats_score_col = "skills_match_score"
    elif "cv_score" in candidate_df.columns:
        ats_score_col = "cv_score"
    else:
        ats_score_col = None

    col4, col5, col6 = st.columns(3)

    with col4:
        if ats_score_col:
            fig = px.histogram(
                candidate_df,
                x=ats_score_col,
                nbins=12,
                title="ATS / Skills Match Score Distribution",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(
                marker_line_color="#2563EB",  # deeper blue,
                marker_line_width=1.2
            )
            render_chart_card(style_chart(fig))
        else:
            st.info("No ATS score column available.")

    with col5:
        if "experience_years" in candidate_df.columns:
            exp_col = "experience_years"
        elif "years_experience" in candidate_df.columns:
            exp_col = "years_experience"
        else:
            exp_col = None

        if exp_col:
            fig = px.histogram(
                candidate_df,
                x=exp_col,
                nbins=10,
                title="Candidate Experience Distribution",
                color_discrete_sequence=["#2563EB"]   # deeper blue
            )
            fig.update_traces(
                marker_line_color="#E5E7EB",
                marker_line_width=1.2
            )
            render_chart_card(style_chart(fig))
        else:
            st.info("No experience column available.")

    with col6:
        if "skills" in candidate_df.columns:
            skills_series = (
                candidate_df["skills"]
                .dropna()
                .astype(str)
                .str.split(",")
                .explode()
                .str.strip()
            )

            skills_df = (
                skills_series
                .value_counts()
                .head(8)
                .reset_index()
            )

            skills_df.columns = ["skill", "count"]

            fig = px.bar(
                skills_df,
                x="count",
                y="skill",
                orientation="h",
                title="Top Skills Detected",
                text="count",
                color_discrete_sequence=[ORANGE]
            )
            fig.update_traces(textposition="outside")
            render_chart_card(style_chart(fig))
        else:
            st.info("No skills column available.")

    st.markdown(
        "<div class='section-title'>AI Job Description Automation</div>",
        unsafe_allow_html=True
    )

    jd_col1, jd_col2 = st.columns([1, 1.4])

    with jd_col1:
        role = st.selectbox(
            "Select Role",
            sorted(candidates_df["role_applied"].unique().tolist())
        )

        department = st.text_input(
            "Department",
            value="Engineering"
        )

        seniority = st.selectbox(
            "Seniority",
            ["Entry-level", "Mid-level", "Senior"]
        )

        generate_jd = st.button("Generate Job Description")

    with jd_col2:
        st.markdown(
            """
            <div class='summary-box'>
                <b>JD Automation Flow:</b><br>
                HR selects a role and seniority level. The AI generates a structured job description,
                which can later be reviewed, approved, and pushed to career pages, LinkedIn, ATS platforms,
                or job boards. Applications received from those platforms then flow into the CV ranking engine.
            </div>
            """,
            unsafe_allow_html=True
        )

    if generate_jd:
        jd = generate_job_description(
            role=role,
            department=department,
            seniority=seniority
        )

        st.text_area(
            "Generated Job Description",
            value=jd,
            height=320
        )

    st.markdown(
        "<div class='section-title'>Candidate Action Center</div>",
        unsafe_allow_html=True
    )

    ranked_df = rank_candidates(role)

    if ranked_df.empty:
        st.info("No candidates found for the selected role.")
    else:
        action_col1, action_col2, action_col3 = st.columns(3)

        with action_col1:
            selected_candidate = st.selectbox(
                "Select Candidate",
                ranked_df["candidate_id"].tolist()
            )

        with action_col2:
            candidate_action = st.selectbox(
                "Action",
                [
                    "Shortlist Candidate",
                    "Schedule Interview",
                    "Move to Offer Stage",
                    "Reject Candidate",
                    "Hire Candidate"
                ]
            )

        with action_col3:
            st.write("")
            st.write("")
            if st.button("Apply Candidate Action"):
                st.success(
                    f"{candidate_action} applied to candidate {selected_candidate}. "
                    "For the demo, this represents automated ATS workflow movement."
                )

        st.dataframe(
            ranked_df.head(15),
            use_container_width=True,
            height=380
        )








    st.markdown(
        "<div class='section-title'>Onboarding Intelligence</div>",
        unsafe_allow_html=True
    )

    onboarding_summary = get_onboarding_summary()
    pending_df = get_pending_tasks()

    onboarding_funnel_df = pd.DataFrame({
        "stage": ["Not Started", "In Progress", "Completed"],
        "count": [
            onboarding_summary.get("not_started", 0),
            onboarding_summary.get("in_progress", 0),
            onboarding_summary.get("completed", 0)
        ]
    })

    onboarding_status_df = pd.DataFrame({
        "status": ["Completed", "In Progress", "Not Started"],
        "count": [
            onboarding_summary.get("completed", 0),
            onboarding_summary.get("in_progress", 0),
            onboarding_summary.get("not_started", 0)
        ]
    })

    total_onboarding = onboarding_status_df["count"].sum()

    onboarding_completion_rate = (
        round((onboarding_summary.get("completed", 0) / total_onboarding) * 100, 1)
        if total_onboarding > 0 else 0
    )

    onboard_col1, onboard_col2, onboard_col3 = st.columns(3)

    with onboard_col1:
        fig = px.funnel(
            onboarding_funnel_df,
            x="count",
            y="stage",
            title="Onboarding Progress Funnel",
            color_discrete_sequence=[ORANGE]
        )
        render_chart_card(style_chart(fig))

    with onboard_col2:
        fig = px.pie(
            onboarding_status_df,
            names="status",
            values="count",
            title="Onboarding Status Distribution",
            hole=0.55,
            color="status",
            color_discrete_map={
                "Completed": "#22C55E",
                "In Progress": "#F59E0B",
                "Not Started": "#64748B"
            }
        )
        render_chart_card(style_chart(fig))

    with onboard_col3:
        gauge_fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=onboarding_completion_rate,
                number={"suffix": "%", "font": {"color": "#FFFFFF", "size": 38}},
                title={"text": "Onboarding Completion Rate", "font": {"color": "#FFFFFF", "size": 16}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#CBD5E1"},
                    "bar": {"color": ORANGE},
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
        "<div class='section-title'>Automated Onboarding Event Flow</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class='summary-box'>
            <b>Production Flow:</b><br>
            In the real system, onboarding status is not manually ticked by HR. 
            Each onboarding activity sends an event into the HR automation system. 
            When a candidate submits documents, completes background verification, finishes e-learning, 
            signs policy documents, or receives system access, the connected service updates the onboarding record automatically.
            <br><br>
            <b>Example:</b> Document Portal → sends document_submitted event → Onboarding Service updates status → Dashboard refreshes.
        </div>
        """,
        unsafe_allow_html=True
    )

    event_col1, event_col2, event_col3 = st.columns(3)

    with event_col1:
        st.metric("Documents Submitted", onboarding_summary.get("completed", 0) + onboarding_summary.get("in_progress", 0))

    with event_col2:
        st.metric("Training Completed", onboarding_summary.get("completed", 0))

    with event_col3:
        st.metric("Access Setup Pending", onboarding_summary.get("not_started", 0) + onboarding_summary.get("in_progress", 0))

    st.markdown(
        "<div class='section-title'>Pending Onboarding Repository</div>",
        unsafe_allow_html=True
    )

    if pending_df.empty:
        st.success("No pending onboarding tasks.")
    else:
        st.dataframe(
            pending_df.head(20),
            use_container_width=True,
            height=360
        )







    st.markdown(
        "<div class='section-title'>AI HR Operational Summary</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class='summary-box'>
            <b>AI HR Recommendation:</b><br>
            The recruitment system is currently processing <b>{intake['total_applications']}</b> applications
            across <b>{intake['roles_receiving_applications']}</b> active roles. Candidate screening shows
            <b>{metrics['shortlisted_candidates']}</b> shortlisted applicants and
            <b>{metrics['interviews_scheduled']}</b> interview-stage candidates. 
            Onboarding completion is currently <b>{onboarding_completion_rate}%</b>. 
            HR should prioritize interview scheduling, pending onboarding tasks, and high-scoring candidates
            for active business-critical roles.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-title'>Candidate Repository</div>",
        unsafe_allow_html=True
    )

    repo_columns = [
        "candidate_id",
        "full_name",
        "role_applied",
        "experience_years",
        "skills_match_score",
        "ai_rank",
        "status",
        "created_at"
    ]

    available_repo_columns = [
        col for col in repo_columns
        if col in candidates_df.columns
    ]

    st.dataframe(
        candidates_df[available_repo_columns].head(50),
        use_container_width=True,
        height=420
    )