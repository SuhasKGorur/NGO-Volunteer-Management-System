# app.py
# Application entry point — configuration, sidebar, routing

import streamlit as st

from database import setup_database
from auth import initialize_session, login, logout, register_ngo

from pages.admin_dashboard import show_admin_dashboard
from pages.ngo_dashboard import show_ngo_dashboard
from pages.volunteer_dashboard import show_volunteer_dashboard
from pages.departments import show_departments
from pages.volunteers import show_volunteers
from pages.events import show_events
from pages.attendance import show_attendance
from pages.profile import show_profile


# ── Page config (must be first Streamlit call) ──────────────────────────────

st.set_page_config(
    page_title="NGO Volunteer Management",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ── Sidebar logo (inline SVG — no external image dependency) ────────────────

SIDEBAR_LOGO_SVG = """
<div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
  <svg width="42" height="42" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="ngoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#6366F1"/>
        <stop offset="100%" stop-color="#8B5CF6"/>
      </linearGradient>
    </defs>
    <circle cx="32" cy="32" r="30" fill="url(#ngoGrad)"/>
    <path d="M20 34c0-7 5-13 12-13s12 6 12 13c0 6-5 10-12 15-7-5-12-9-12-15z"
          fill="white" opacity="0.95"/>
    <circle cx="26" cy="24" r="3.2" fill="white" opacity="0.95"/>
    <circle cx="38" cy="24" r="3.2" fill="white" opacity="0.95"/>
  </svg>
  <div>
    <div style="font-weight:800; font-size:1.05rem; color:white; line-height:1.1;">NGO System</div>
    <div style="font-size:0.72rem; color:rgba(255,255,255,0.75);">Volunteer Management</div>
  </div>
</div>
"""


def apply_styles():
    """Inject global CSS for a modern, cohesive look across the app."""

    st.markdown("""
    <style>

    /* ── App-wide metric cards ─────────────────────────────────────── */
    div[data-testid="metric-container"],
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(99,102,241,0.02));
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 14px;
        padding: 12px;
    }

    h1, h2, h3 {
        color: #4338CA;
    }

    /* ── Buttons ────────────────────────────────────────────────────── */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.15s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(99,102,241,0.18);
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
        border: none !important;
    }

    /* ── Tabs ───────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid rgba(120,120,120,0.15);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 8px 18px;
        font-weight: 600;
        color: rgba(90,90,90,0.85);
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.06));
        color: #4338CA !important;
        border-bottom: 3px solid #6366F1;
    }

    /* ── Expanders ──────────────────────────────────────────────────── */
    div[data-testid="stExpander"] {
        border-radius: 14px !important;
        border: 1px solid rgba(120,120,120,0.15) !important;
        overflow: hidden;
    }

    /* ── Sidebar ────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #4338CA 0%, #6366F1 45%, #7C3AED 100%);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2) !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.18);
        color: white !important;
        text-align: left;
        justify-content: flex-start;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.18);
        border-color: rgba(255,255,255,0.35);
    }

    section[data-testid="stSidebar"] button[kind="primary"] {
        background: rgba(255,255,255,0.95) !important;
        color: #4338CA !important;
        border: none !important;
        font-weight: 700;
    }

    /* ── Misc chrome ────────────────────────────────────────────────── */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """, unsafe_allow_html=True)


# ── Sidebar builders ────────────────────────────────────────────────────────

def navbutton(label, target):
    """Render a single sidebar nav button, highlighted if it's the active page."""

    is_active = st.session_state.page == target

    if st.sidebar.button(
        label,
        use_container_width=True,
        key=f"sb_{target}",
        type="primary" if is_active else "secondary"
    ):
        st.session_state.page = target
        st.rerun()


def sidebaradmin():

    st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
    st.sidebar.caption("Role: Administrator")
    st.sidebar.markdown("---")

    pages = {
        "📊 Dashboard": "admin_dashboard",
        "🏛️ Departments": "departments",
        "👥 All Volunteers": "volunteers",
    }

    for label, target in pages.items():
        navbutton(label, target)


def sidebarngo():

    st.sidebar.markdown(f"### 🏢 {st.session_state.user_name}")
    st.sidebar.caption("Role: NGO")
    st.sidebar.markdown("---")

    pages = {
        "📊 Dashboard": "ngo_dashboard",
        "👥 Volunteers": "volunteers",
        "📅 Events": "events",
        "✅ Attendance": "attendance",
    }

    for label, target in pages.items():
        navbutton(label, target)


def sidebarvolunteer():

    st.sidebar.markdown(f"### 🙋 {st.session_state.user_name}")
    st.sidebar.caption("Role: Volunteer")
    st.sidebar.markdown("---")

    pages = {
        "📊 Dashboard": "volunteer_dashboard",
        "👤 My Profile": "profile",
    }

    for label, target in pages.items():
        navbutton(label, target)


def render_sidebar():
    """Show role-specific sidebar + logout."""

    st.sidebar.markdown(SIDEBAR_LOGO_SVG, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    role = st.session_state.role

    if role == "admin":
        sidebaradmin()

    elif role == "ngo":
        sidebarngo()

    elif role == "volunteer":
        sidebarvolunteer()

    st.sidebar.markdown("---")

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):
        logout()


# ── Router ──────────────────────────────────────────────────────────────────

def route():
    """Direct to the correct page module."""

    page = st.session_state.page
    role = st.session_state.role

    if role == "admin":

        if page == "departments":
            show_departments()

        elif page == "volunteers":
            show_volunteers()

        else:
            show_admin_dashboard()

    elif role == "ngo":

        if page == "volunteers":
            show_volunteers()

        elif page == "events":
            show_events()

        elif page == "attendance":
            show_attendance()

        else:
            show_ngo_dashboard()

    elif role == "volunteer":

        if page == "profile":
            show_profile()

        else:
            show_volunteer_dashboard()


# ── Main ────────────────────────────────────────────────────────────────────

def main():

    apply_styles()
    setup_database()
    initialize_session()

    if not st.session_state.logged_in:

        if st.session_state.page == "ngo_registration":
            register_ngo()

        else:
            login()

        return

    render_sidebar()
    route()


if __name__ == "__main__":
    main()