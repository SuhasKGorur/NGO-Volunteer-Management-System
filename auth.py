# auth.py
# Session management, login, logout, NGO registration

import streamlit as st
from database import fetch_one, execute_query


HERO_LOGO_SVG = """
<div style="display:flex; flex-direction:column; align-items:center; margin-bottom:0.5rem;">
  <svg width="72" height="72" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="ngoGradHero" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#6366F1"/>
        <stop offset="100%" stop-color="#8B5CF6"/>
      </linearGradient>
    </defs>
    <circle cx="32" cy="32" r="30" fill="url(#ngoGradHero)"/>
    <path d="M20 34c0-7 5-13 12-13s12 6 12 13c0 6-5 10-12 15-7-5-12-9-12-15z"
          fill="white" opacity="0.95"/>
    <circle cx="26" cy="24" r="3.2" fill="white" opacity="0.95"/>
    <circle cx="38" cy="24" r="3.2" fill="white" opacity="0.95"/>
  </svg>
</div>
"""


def inject_auth_css():
    st.markdown(
        """
        <style>
        .auth-title {
            text-align: center;
            background: linear-gradient(135deg, #6366F1, #8B5CF6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem;
            font-weight: 800;
            margin: 0 0 0.2rem 0;
        }
        .auth-subtitle {
            text-align: center;
            color: rgba(120,120,120,0.9);
            font-size: 0.95rem;
            margin-bottom: 1.6rem;
        }
        div[data-testid="stForm"] {
            border: 1px solid rgba(120,120,120,0.15);
            border-radius: 18px;
            padding: 1.5rem 1.7rem 1rem 1.7rem;
            box-shadow: 0 6px 20px rgba(99,102,241,0.08);
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            justify-content: center;
            border-bottom: 1px solid rgba(120,120,120,0.15);
            margin-bottom: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 8px 22px;
            font-weight: 600;
            color: rgba(90,90,90,0.85);
            background: transparent;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.06));
            color: #4338CA !important;
            border-bottom: 3px solid #6366F1;
        }
        .auth-role-caption {
            text-align: center;
            font-size: 0.85rem;
            color: rgba(120,120,120,0.85);
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session():
    """Set default session state variables."""

    defaults = {
        "logged_in": False,
        "user_id": None,
        "user_name": None,
        "role": None,
        "page": "login"
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def login():
    """Render login form and authenticate user."""

    inject_auth_css()

    st.markdown(HERO_LOGO_SVG, unsafe_allow_html=True)
    st.markdown(
        "<div class='auth-title'>NGO Volunteer Management System</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='auth-subtitle'>Sign in to manage volunteers, events and attendance.</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:

        tab_admin, tab_ngo, tab_vol = st.tabs(
            ["🛡️ Admin", "🏢 NGO", "🙋 Volunteer"]
        )

        with tab_admin:
            _login_tab("admin", "🛡️ Admin Login")

        with tab_ngo:
            _login_tab("ngo", "🏢 NGO Login")

        with tab_vol:
            _login_tab("volunteer", "🙋 Volunteer Login")

        st.markdown("---")
        st.markdown(
            "<p style='text-align:center;'><b>Don't have an account? Register your NGO below.</b></p>",
            unsafe_allow_html=True,
        )

        if st.button(
            "📋 Register Your NGO",
            use_container_width=True
        ):
            st.session_state.page = "ngo_registration"
            st.rerun()


def _login_tab(role, heading):
    """Render one role's login form inside its tab and authenticate on submit."""

    st.markdown(
        f"<div class='auth-role-caption'>{heading}</div>",
        unsafe_allow_html=True,
    )

    with st.form(f"login_form_{role}"):
        email = st.text_input("📧 Email Address", key=f"email_{role}")
        password = st.text_input(
            "🔒 Password",
            type="password",
            key=f"password_{role}"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
            type="primary",
        )

        if submitted:

            if not email or not password:
                st.warning("Please enter both email and password.")
                return

            _authenticate(
                role,
                email.strip(),
                password
            )


def _authenticate(role, email, password):
    """Validate credentials and set session on success."""

    if role == "admin":

        user = fetch_one(
            "SELECT * FROM admins WHERE email=%s AND password=%s",
            (email, password)
        )

        if user:
            setsession(
                "admin",
                user["admin_id"],
                user["admin_name"]
            )
        else:
            st.error("❌ Invalid admin credentials.")

    elif role == "ngo":

        user = fetch_one(
            "SELECT * FROM ngos WHERE email=%s AND password=%s",
            (email, password)
        )

        if user:

            if user["status"] == "Approved":
                setsession(
                    "ngo",
                    user["ngo_id"],
                    user["ngo_name"]
                )

            elif user["status"] == "Pending":
                st.warning("⏳ Your registration is pending admin approval.")

            else:
                st.error("❌ Your registration was rejected.")

        else:
            st.error("❌ Invalid NGO credentials.")

    elif role == "volunteer":

        user = fetch_one(
            "SELECT * FROM volunteers WHERE email=%s AND password=%s",
            (email, password)
        )

        if user:
            setsession(
                "volunteer",
                user["volunteer_id"],
                user["volunteer_name"]
            )
        else:
            st.error("❌ Invalid volunteer credentials.")


def setsession(role, user_id, user_name):
    """Write session state after successful login."""

    st.session_state.logged_in = True
    st.session_state.role = role
    st.session_state.user_id = user_id
    st.session_state.user_name = user_name
    st.session_state.page = f"{role}_dashboard"

    st.rerun()


def logout():
    """Destroy session and return to login."""

    for key in list(st.session_state.keys()):
        del st.session_state[key]

    st.rerun()


def register_ngo():
    """Render NGO self-registration form."""

    inject_auth_css()

    st.markdown(HERO_LOGO_SVG, unsafe_allow_html=True)
    st.markdown(
        "<div class='auth-title'>NGO Volunteer Management System</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='auth-subtitle'>Register your organization to get started.</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])

    with col2:

        st.markdown("### 📋 Register Your NGO")

        st.info(
            "After registration, an admin will review and approve your account."
        )

        with st.form("register_form"):

            ngo_name = st.text_input("NGO Name *")

            rc1, rc2 = st.columns(2)
            registration_no = rc1.text_input("Registration Number *")
            phone = rc2.text_input("Phone Number")

            email = st.text_input("Email Address *")
            address = st.text_area("Address")

            pc1, pc2 = st.columns(2)
            password = pc1.text_input(
                "Password *",
                type="password"
            )
            confirm = pc2.text_input(
                "Confirm Password *",
                type="password"
            )

            submitted = st.form_submit_button(
                "Submit Registration",
                use_container_width=True,
                type="primary",
            )

            if submitted:

                if not all([
                    ngo_name,
                    registration_no,
                    email,
                    password,
                    confirm
                ]):
                    st.warning("Please fill all required fields (*).")
                    return

                if password != confirm:
                    st.error("Passwords do not match.")
                    return

                if len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                    return

                existing = fetch_one(
                    "SELECT ngo_id FROM ngos WHERE email=%s OR registration_no=%s",
                    (email, registration_no)
                )

                if existing:
                    st.error(
                        "Email or Registration Number already exists."
                    )
                    return

                ok = execute_query(
                    """
                    INSERT INTO ngos
                    (
                        ngo_name,
                        registration_no,
                        email,
                        phone,
                        address,
                        password
                    )
                    VALUES
                    (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        ngo_name,
                        registration_no,
                        email,
                        phone,
                        address,
                        password
                    )
                )

                if ok:
                    st.success(
                        "✅ Registration submitted! Wait for admin approval."
                    )
                else:
                    st.error(
                        "Registration failed. Please try again."
                    )

        st.markdown("---")

        if st.button(
            "← Back to Login",
            use_container_width=True
        ):
            st.session_state.page = "login"
            st.rerun()