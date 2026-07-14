# pages/ngo_dashboard.py
# NGO dashboard — own stats, volunteers, events summary

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
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .list-card {
            border: 1px solid rgba(120,120,120,0.15);
            border-radius: 12px;
            padding: 0.7rem 0.95rem;
            margin-bottom: 0.6rem;
        }
        .list-card-title {
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 2px;
        }
        .list-card-caption {
            font-size: 0.8rem;
            color: rgba(120,120,120,0.85);
        }
        .badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: rgba(99,102,241,0.12);
            color: #6366F1;
        }
        .badge-muted {
            background: rgba(120,120,120,0.12);
            color: rgba(120,120,120,0.9);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_ngo_dashboard():

    ngo_id = st.session_state.user_id

    inject_css()

    st.markdown(
        f"""
        <div class="dash-hero">
            <h1>📊 Dashboard — {st.session_state.user_name}</h1>
            <p>An overview of your volunteers, events and attendance activity.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics(ngo_id)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        upcomingevents(ngo_id)

    with col2:
        recentvolunteers(ngo_id)

    st.write("")

    attendancesummary(ngo_id)


# ── Metrics ──────────────────────────────────────────────────────────────────

def metrics(ngo_id):

    c1, c2, c3, c4 = st.columns(4)

    r = fetch_one(
        "SELECT COUNT(*) AS n FROM volunteers WHERE ngo_id=%s",
        (ngo_id,)
    )
    c1.metric("👥 My Volunteers", r["n"] if r else 0)

    r = fetch_one(
        "SELECT COUNT(*) AS n FROM events WHERE ngo_id=%s",
        (ngo_id,)
    )
    c2.metric("📅 Total Events", r["n"] if r else 0)

    r = fetch_one(
        """
        SELECT COUNT(*) AS n
        FROM events
        WHERE ngo_id=%s
          AND event_status='Upcoming'
        """,
        (ngo_id,)
    )
    c3.metric("🔔 Upcoming Events", r["n"] if r else 0)

    r = fetch_one(
        """
        SELECT COUNT(*) AS n
        FROM attendance a
        INNER JOIN events e
            ON a.event_id = e.event_id
        WHERE e.ngo_id=%s
          AND a.attendance_status='Present'
        """,
        (ngo_id,)
    )
    c4.metric("✅ Total Present Records", r["n"] if r else 0)


# ── Upcoming Events ──────────────────────────────────────────────────────────

def upcomingevents(ngo_id):

    st.markdown(
        "<div class='section-title'>📅 Upcoming Events</div>",
        unsafe_allow_html=True,
    )

    rows = fetch_all(
        """
        SELECT
            event_name,
            event_date,
            location
        FROM events
        WHERE ngo_id=%s
          AND event_status='Upcoming'
        ORDER BY event_date ASC
        LIMIT 5
        """,
        (ngo_id,)
    )

    if not rows:
        st.info("No upcoming events.")
        return

    for event in rows:
        st.markdown(
            f"""
            <div class="list-card">
                <div class="list-card-title">{event['event_name']}</div>
                <div class="list-card-caption">
                    📆 {event['event_date']} &nbsp;·&nbsp; 📍 {event['location'] or '—'}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Recent Volunteers ────────────────────────────────────────────────────────

def recentvolunteers(ngo_id):

    st.markdown(
        "<div class='section-title'>👥 Recently Added Volunteers</div>",
        unsafe_allow_html=True,
    )

    rows = fetch_all(
        """
        SELECT
            v.volunteer_name,
            d.department_name,
            v.joining_date
        FROM volunteers v
        LEFT JOIN departments d
            ON v.department_id = d.department_id
        WHERE v.ngo_id=%s
        ORDER BY v.created_at DESC
        LIMIT 5
        """,
        (ngo_id,)
    )

    if not rows:
        st.info("No volunteers yet.")
        return

    for volunteer in rows:

        dept_badge = (
            f"<span class='badge'>{volunteer['department_name']}</span>"
            if volunteer["department_name"]
            else "<span class='badge badge-muted'>No Dept</span>"
        )

        st.markdown(
            f"""
            <div class="list-card">
                <div class="list-card-title">{volunteer['volunteer_name']}</div>
                <div class="list-card-caption">
                    {dept_badge} &nbsp;·&nbsp; 📅 Joined: {volunteer['joining_date'] or '—'}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Attendance Summary ───────────────────────────────────────────────────────

def attendancesummary(ngo_id):

    st.markdown(
        "<div class='section-title'>📋 Attendance Summary by Event</div>",
        unsafe_allow_html=True,
    )

    rows = fetch_all(
        """
        SELECT
            e.event_name,
            e.event_date,
            COUNT(a.attendance_id) AS total_marked,
            SUM(a.attendance_status = 'Present') AS present,
            SUM(a.attendance_status = 'Absent') AS absent
        FROM events e
        LEFT JOIN attendance a
            ON a.event_id = e.event_id
        WHERE e.ngo_id=%s
        GROUP BY e.event_id
        ORDER BY e.event_date DESC
        LIMIT 10
        """,
        (ngo_id,)
    )

    if not rows:
        st.info("No attendance records yet.")
        return

    for row in rows:

        with st.expander(
            f"📅 {row['event_name']}  ·  {row['event_date']}"
        ):

            c1, c2, c3 = st.columns(3)

            c1.metric("Total Marked", row["total_marked"])
            c2.metric("✅ Present", row["present"] or 0)
            c3.metric("❌ Absent", row["absent"] or 0)

            total = row["total_marked"] or 0
            present = row["present"] or 0
            pct = round((present / total) * 100, 1) if total > 0 else 0

            st.progress(min(int(pct), 100) / 100)
            st.caption(f"{pct}% attendance for this event")