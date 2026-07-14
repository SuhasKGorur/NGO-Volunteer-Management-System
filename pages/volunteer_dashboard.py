# pages/volunteer_dashboard.py
# Volunteer's personal dashboard — summary, events, attendance

import streamlit as st
from database import fetch_all, fetch_one


def inject_css():
    st.markdown(
        """
        <style>
        .dash-hero {
            background: linear-gradient(135deg, rgba(99,102,241,0.10), rgba(99,102,241,0.02));
            border: 1px solid rgba(99,102,241,0.15);
            border-radius: 18px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1.4rem;
        }
        .dash-hero h1 {
            margin: 0 0 0.15rem 0;
            font-size: 1.7rem;
        }
        .dash-hero p {
            margin: 0;
            color: rgba(120,120,120,0.9);
            font-size: 0.95rem;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(99,102,241,0.02));
            border: 1px solid rgba(99,102,241,0.15);
            border-radius: 14px;
            padding: 0.9rem 1rem;
        }
        div[data-testid="stExpander"] {
            border-radius: 14px !important;
            border: 1px solid rgba(120,120,120,0.15) !important;
            overflow: hidden;
            margin-bottom: 0.6rem;
        }
        div[data-testid="stExpander"] summary {
            font-weight: 600;
        }
        .section-title {
            font-weight: 700;
            font-size: 1.05rem;
            margin-bottom: 0.6rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .attendance-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(120,120,120,0.15);
            border-radius: 12px;
            padding: 0.6rem 0.9rem;
            margin-bottom: 0.5rem;
        }
        .attendance-left {
            display: flex;
            flex-direction: column;
        }
        .attendance-event {
            font-weight: 600;
            font-size: 0.92rem;
        }
        .attendance-date {
            font-size: 0.78rem;
            color: rgba(120,120,120,0.85);
        }
        .status-pill {
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            white-space: nowrap;
        }
        .status-present {
            background: rgba(34,197,94,0.12);
            color: #16A34A;
        }
        .status-absent {
            background: rgba(239,68,68,0.12);
            color: #DC2626;
        }
        .marked-caption {
            font-size: 0.72rem;
            color: rgba(120,120,120,0.7);
            margin: -0.3rem 0 0.6rem 0.1rem;
        }
        .event-meta {
            font-size: 0.85rem;
            margin-bottom: 0.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_volunteer_dashboard():

    vol_id = st.session_state.user_id

    inject_css()

    st.markdown(
        f"""
        <div class="dash-hero">
            <h1>📊 Welcome, {st.session_state.user_name}!</h1>
            <p>Here's a quick look at your activity and upcoming events.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics(vol_id)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        upcomingevents(vol_id)

    with col2:
        myattendance(vol_id)


# ── Metrics ──────────────────────────────────────────────────────────────────

def metrics(vol_id):

    c1, c2, c3 = st.columns(3)

    r = fetch_one(
        "SELECT COUNT(*) AS n FROM attendance WHERE volunteer_id=%s",
        (vol_id,)
    )
    c1.metric("📋 Events Attended", r["n"] if r else 0)

    r = fetch_one(
        """
        SELECT COUNT(*) AS n
        FROM attendance
        WHERE volunteer_id=%s
          AND attendance_status='Present'
        """,
        (vol_id,)
    )

    present = r["n"] if r else 0
    c2.metric("✅ Present Count", present)

    total_r = fetch_one(
        "SELECT COUNT(*) AS n FROM attendance WHERE volunteer_id=%s",
        (vol_id,)
    )

    total = total_r["n"] if total_r else 0

    pct = round((present / total) * 100, 1) if total > 0 else 0

    c3.metric("📈 Attendance %", f"{pct}%")

    st.progress(min(int(pct), 100) / 100)


# ── Upcoming Events ──────────────────────────────────────────────────────────

def upcomingevents(vol_id):

    st.markdown(
        "<div class='section-title'>📅 Upcoming Events (My NGO)</div>",
        unsafe_allow_html=True,
    )

    # Fetch NGO of this volunteer
    vol = fetch_one(
        "SELECT ngo_id FROM volunteers WHERE volunteer_id=%s",
        (vol_id,)
    )

    if not vol:
        st.info("Volunteer info not found.")
        return

    rows = fetch_all(
        """
        SELECT
            event_name,
            event_date,
            location,
            description
        FROM events
        WHERE ngo_id=%s
          AND event_status='Upcoming'
        ORDER BY event_date ASC
        LIMIT 5
        """,
        (vol["ngo_id"],)
    )

    if not rows:
        st.info("No upcoming events.")
        return

    for event in rows:

        with st.expander(
            f"📌 {event['event_name']}  ·  {event['event_date']}"
        ):
            st.markdown(
                f"<div class='event-meta'>📍 <b>Location:</b> {event['location'] or '—'}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='event-meta'>📝 <b>Details:</b> {event['description'] or '—'}</div>",
                unsafe_allow_html=True,
            )


# ── My Attendance ────────────────────────────────────────────────────────────

def myattendance(vol_id):

    st.markdown(
        "<div class='section-title'>✅ My Attendance History</div>",
        unsafe_allow_html=True,
    )

    rows = fetch_all(
        """
        SELECT
            e.event_name,
            e.event_date,
            a.attendance_status,
            a.marked_on
        FROM attendance a
        INNER JOIN events e
            ON a.event_id = e.event_id
        WHERE a.volunteer_id=%s
        ORDER BY e.event_date DESC
        LIMIT 10
        """,
        (vol_id,)
    )

    if not rows:
        st.info("No attendance records yet.")
        return

    for row in rows:

        is_present = row["attendance_status"] == "Present"
        status_icon = "✅" if is_present else "❌"
        pill_class = "status-present" if is_present else "status-absent"

        st.markdown(
            f"""
            <div class="attendance-row">
                <div class="attendance-left">
                    <span class="attendance-event">{row['event_name']}</span>
                    <span class="attendance-date">{row['event_date']}</span>
                </div>
                <span class="status-pill {pill_class}">{status_icon} {row['attendance_status']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='marked-caption'>Marked on: {row['marked_on']}</div>",
            unsafe_allow_html=True,
        )