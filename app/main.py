import streamlit as st

#from app.pages.customer_operations import render_customer_operations
#from app.pages.hr_automation import render_hr_automation
#from app.pages.devsecops_monitoring import render_devsecops_monitoring
#from app.pages.executive_dashboard import render_executive_dashboard
#from app.chatbot.chat_interface import render_chat_interface
from app.pages.customer_operations import render_customer_operations
from app.pages.hr_automation import render_hr_automation
from app.pages.devsecops_monitoring import render_devsecops_monitoring
from app.pages.executive_dashboard import render_executive_dashboard



st.set_page_config(
    page_title="Waya AI Process Automation",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F172A 0%, #111827 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        .sidebar-title {
            font-size: 28px;
            font-weight: 900;
            color: #FFFFFF;
            margin-bottom: 0px;
        }

        .sidebar-subtitle {
            font-size: 15px;
            color: #F97316;
            font-weight: 700;
            margin-bottom: 30px;
        }

        .sidebar-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-left: 4px solid #F97316;
            border-radius: 14px;
            padding: 16px;
            margin-top: 40px;
            color: #E5E7EB;
            font-size: 14px;
        }

        .sidebar-card-title {
            color: #FFFFFF;
            font-weight: 800;
            font-size: 16px;
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("<div class='sidebar-title'>Waya AI</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-subtitle'>Process Automation Platform</div>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Main Navigation",
    [
        "Executive Dashboard",
       # "Customer Chatbot",
        "Customer Operations",
        "HR Automation",
        "DevSecOps Monitoring"
    ]
)

st.sidebar.markdown(
    """
    <div class="sidebar-card">
        <div class="sidebar-card-title">AI-Powered Operations</div>
        Intelligent automation across customer support, HR, and technical operations.
    </div>
    """,
    unsafe_allow_html=True
)

if page == "Executive Dashboard":
    render_executive_dashboard()

#elif page == "Customer Chatbot":
    # render_chat_interface()

elif page == "Customer Operations":
    render_customer_operations()

elif page == "HR Automation":
    render_hr_automation()

elif page == "DevSecOps Monitoring":
    render_devsecops_monitoring()

st.sidebar.markdown(
    """
    <div style="
        position: fixed;
        bottom: 25px;
        left: 22px;
        width: 300px;
        padding: 14px 16px;
        border-radius: 14px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 4px solid #F97316;
        color: #CBD5E1;
        font-size: 13px;
        line-height: 1.6;
    ">
        <b style="color:#FFFFFF;">Designed by Jimmy</b><br>
        Waya AI Process Automation Platform · 2026
    </div>
    """,
    unsafe_allow_html=True
)