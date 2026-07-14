# pages/admin_dashboard.py
# Admin overview: metrics, NGO approval, NGO listings

import streamlit as st
import pandas as pd
from database import fetch_all, fetch_one, execute_query


def inject_css():
    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(99,102,241,0.02));
            border-radius: 14px;
            padding: 0.9rem 1rem;
        }
        div[data-testid="stExpander"] {
            border-radius: 14px !important;
            border: 1px solid rgba(120,120,120,0.15) !important;
            overflow: hidden;
        }
        .summary-card {
            background: white;
            border: 1px solid rgba(120,120,120,0.12);
            padding: 1.1rem 1.2rem 0.4rem 1.2rem;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.05);
            margin-bottom: 0.8rem;
        }
        .summary-card h4 {
            margin: 0 0 0.6rem 0;
            color: #6366F1;
            font-size: 1rem;
        }
        .ngo-card-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.15rem;
        }
        .status-pill {
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            white-space: nowrap;
        }
        .status-pending {
            background: rgba(234,179,8,0.14);
            color: #B45309;
        }
        .status-approved {
            background: rgba(34,197,94,0.12);
            color: #16A34A;
        }
        .status-rejected {
            background: rgba(239,68,68,0.12);
            color: #DC2626;
        }
        .vol-field-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            color: rgba(120,120,120,0.8);
            margin-bottom: -0.2rem;
        }
        .vol-field-value {
            font-size: 0.92rem;
            margin-bottom: 0.55rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def field(col, label, value):
    col.markdown(f"<div class='vol-field-label'>{label}</div>", unsafe_allow_html=True)
    col.markdown(f"<div class='vol-field-value'>{value}</div>", unsafe_allow_html=True)


def show_admin_dashboard():

    inject_css()

    st.markdown("""
    <div style="
        background:linear-gradient(135deg,#6366F1,#8B5CF6);
        padding:30px;
        border-radius:18px;
        color:white;
        margin-bottom:25px;
        box-shadow:0 8px 18px rgba(0,0,0,.15);
    ">

    <h1 style="color:white;margin:0;">
        📊 Admin Dashboard
    </h1>

    <p style="margin-top:8px;font-size:17px;opacity:0.95;">
        Monitor NGOs, Volunteers, Departments and Events
    </p>

    </div>
    """, unsafe_allow_html=True)

    _metrics()

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([2,1])

    with right:
        _quick_summary()

    with left:

        tab1, tab2, tab3 = st.tabs(
            [
                "⏳ Pending",
                "✅ Approved",
                "❌ Rejected"
            ]
        )

        with tab1:
            pendingngos()

        with tab2:
            approvedngos()

        with tab3:
            rejectedngos()


# ── Metrics ──────────────────────────────────────────────────────────────────

def _metrics():

    ngo = fetch_one("SELECT COUNT(*) n FROM ngos")["n"]

    pending = fetch_one(
        "SELECT COUNT(*) n FROM ngos WHERE status='Pending'"
    )["n"]

    volunteer = fetch_one(
        "SELECT COUNT(*) n FROM volunteers"
    )["n"]

    department = fetch_one(
        "SELECT COUNT(*) n FROM departments"
    )["n"]

    event = fetch_one(
        "SELECT COUNT(*) n FROM events"
    )["n"]

    upcoming = fetch_one(
        "SELECT COUNT(*) n FROM events WHERE event_status='Upcoming'"
    )["n"]

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "🏢 NGOs",
        ngo,
        border=True
    )

    c2.metric(
        "👥 Volunteers",
        volunteer,
        border=True
    )

    c3.metric(
        "🏛 Departments",
        department,
        border=True
    )

    c4,c5,c6 = st.columns(3)

    c4.metric(
        "📅 Events",
        event,
        border=True
    )

    c5.metric(
        "🔔 Upcoming",
        upcoming,
        border=True
    )

    c6.metric(
        "⏳ Pending",
        pending,
        border=True
    )


def _quick_summary():

    st.markdown("""
    <div class="summary-card">
    <h4>📌 System Summary</h4>
    </div>
    """, unsafe_allow_html=True)

    ngo = fetch_one("SELECT COUNT(*) n FROM ngos")
    vol = fetch_one("SELECT COUNT(*) n FROM volunteers")
    dept = fetch_one("SELECT COUNT(*) n FROM departments")
    event = fetch_one("SELECT COUNT(*) n FROM events")

    df = pd.DataFrame(
        {
            "Count":[
                ngo["n"],
                vol["n"],
                dept["n"],
                event["n"]
            ]
        },
        index=[
            "NGOs",
            "Volunteers",
            "Departments",
            "Events"
        ]
    )

    st.bar_chart(df)
# ── Pending NGOs ─────────────────────────────────────────────────────────────

def pendingngos():

    st.markdown("### ⏳ NGOs Awaiting Approval")

    rows = fetch_all("""
        SELECT ngo_id,
               ngo_name,
               registration_no,
               email,
               phone,
               address,
               created_at
        FROM ngos
        WHERE status = 'Pending'
        ORDER BY created_at DESC
    """)

    if not rows:
        st.info("No pending registrations.")
        return

    for ngo in rows:

        with st.container(border=True):

            st.markdown(
                f"""
                <div class="ngo-card-title">
                    <h3 style="margin:0;">🏢 {ngo['ngo_name']}</h3>
                    <span class="status-pill status-pending">⏳ Pending</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(f"Registration : {ngo['registration_no']}")

            col1, col2 = st.columns(2)

            field(col1, "Email", ngo["email"])
            field(col1, "Phone", ngo["phone"] or "—")

            field(col2, "Address", ngo["address"] or "—")
            field(col2, "Applied", ngo["created_at"])

            ca, cb, _ = st.columns([1, 1, 3])

            if ca.button(
                "✅ Approve",
                key=f"apr_{ngo['ngo_id']}",
                use_container_width=True,
            ):
                approve(ngo["ngo_id"])

            if cb.button(
                "❌ Reject",
                key=f"rej_{ngo['ngo_id']}",
                use_container_width=True,
            ):
                reject(ngo["ngo_id"])


def approve(ngo_id):

    ok = execute_query(
        """
        UPDATE ngos
        SET status='Approved',
            approved_by=%s
        WHERE ngo_id=%s
        """,
        (
            st.session_state.user_id,
            ngo_id
        )
    )

    if ok:
        st.success("NGO approved!")
        st.rerun()

    else:
        st.error("Action failed.")


def reject(ngo_id):

    ok = execute_query(
        """
        UPDATE ngos
        SET status='Rejected'
        WHERE ngo_id=%s
        """,
        (ngo_id,)
    )

    if ok:
        st.warning("NGO rejected.")
        st.rerun()

    else:
        st.error("Action failed.")


# ── Approved NGOs ────────────────────────────────────────────────────────────

def approvedngos():

    st.markdown("### ✅ Approved NGOs")

    search = st.text_input(
        "🔍 Search by name",
        key="srch_appr",
        placeholder="Type an NGO name to filter…",
    )

    rows = fetch_all("""
        SELECT
            n.ngo_id,
            n.ngo_name,
            n.registration_no,
            n.email,
            n.phone,
            n.created_at,
            COUNT(v.volunteer_id) AS vol_count
        FROM ngos n
        LEFT JOIN volunteers v
            ON v.ngo_id = n.ngo_id
        WHERE n.status = 'Approved'
        GROUP BY n.ngo_id
        ORDER BY n.ngo_name
    """)

    if not rows:
        st.info("No approved NGOs yet.")
        return

    for ngo in rows:

        if search and search.lower() not in ngo["ngo_name"].lower():
            continue

        with st.container(border=True):

            st.markdown(
                f"""
                <div class="ngo-card-title">
                    <h3 style="margin:0;">🏢 {ngo['ngo_name']}</h3>
                    <span class="status-pill status-approved">✅ Approved</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(f"Volunteers : {ngo['vol_count']}")

            col1, col2 = st.columns(2)

            field(col1, "Reg No", ngo["registration_no"])
            field(col1, "Email", ngo["email"])

            field(col2, "Phone", ngo["phone"] or "—")
            field(col2, "Joined", ngo["created_at"])


# ── Rejected NGOs ────────────────────────────────────────────────────────────

def rejectedngos():

    st.markdown("### ❌ Rejected NGOs")

    rows = fetch_all("""
        SELECT
            ngo_id,
            ngo_name,
            registration_no,
            email,
            created_at
        FROM ngos
        WHERE status = 'Rejected'
        ORDER BY created_at DESC
    """)

    if not rows:
        st.info("No rejected NGOs.")
        return

    for ngo in rows:

        with st.container(border=True):

            st.markdown(
                f"""
                <div class="ngo-card-title">
                    <h3 style="margin:0;">🏢 {ngo['ngo_name']}</h3>
                    <span class="status-pill status-rejected">❌ Rejected</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(f"Registration : {ngo['registration_no']}")

            col1, col2 = st.columns(2)

            field(col1, "Email", ngo["email"])
            field(col2, "Applied", ngo["created_at"])

            if st.button(
                "🔄 Re-Approve",
                key=f"reappr_{ngo['ngo_id']}",
                use_container_width=True,
            ):
                approve(ngo["ngo_id"])