# pages/profile.py
# Volunteer: view own profile, attendance history, upcoming events

import streamlit as st
from database import fetch_all, fetch_one


def inject_css():
    st.markdown(
        """
        <style>
        .profile-hero {
            display: flex;
            align-items: center;
            gap: 1rem;
            background: linear-gradient(135deg, rgba(99,102,241,0.10), rgba(99,102,241,0.02));
            border: 1px solid rgba(99,102,241,0.15);
            border-radius: 18px;
            padding: 1.3rem 1.6rem;
            margin-bottom: 1.4rem;
        }
        .profile-avatar {
            width: 56px;
            height: 56px;
            min-width: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366F1, #8B5CF6);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            font-weight: 700;
        }
        .profile-hero h2 {
            margin: 0;
            font-size: 1.4rem;
        }
        .profile-hero p {
            margin: 0.15rem 0 0 0;
            color: rgba(120,120,120,0.9);
            font-size: 0.9rem;
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
        .info-card {
            border: 1px solid rgba(120,120,120,0.15);
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.8rem;
        }
        .info-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            color: rgba(120,120,120,0.8);
            margin-bottom: 2px;
        }
        .info-value {
            font-size: 0.98rem;
            font-weight: 500;
            margin-bottom: 0.85rem;
        }
        .info-value:last-child {
            margin-bottom: 0;
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
        .dept-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            background: rgba(99,102,241,0.12);
            color: #6366F1;
        }
        .dept-badge-muted {
            background: rgba(120,120,120,0.12);
            color: rgba(120,120,120,0.9);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_profile():

    vol_id = st.session_state.user_id

    inject_css()

    st.markdown("# 👤 My Profile")
    st.markdown(
        "<p style='color:rgba(120,120,120,0.9); margin-top:-0.5rem;'>"
        "A snapshot of your details, activity and what's coming up.</p>",
        unsafe_allow_html=True,
    )

    profiledetails(vol_id)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        attendancehistory(vol_id)

    with col2:
        upcomingevents(vol_id)


# ── Profile Details ──────────────────────────────────────────────────────────

def profiledetails(vol_id):

    vol = fetch_one(
        """
        SELECT
            v.volunteer_id,
            v.volunteer_name,
            v.gender,
            v.age,
            v.phone,
            v.email,
            v.joining_date,
            v.created_at,
            d.department_name,
            n.ngo_name
        FROM volunteers v
        LEFT JOIN departments d
            ON v.department_id = d.department_id
        INNER JOIN ngos n
            ON v.ngo_id = n.ngo_id
        WHERE v.volunteer_id=%s
        """,
        (vol_id,)
    )

    if not vol:
        st.error("Profile not found.")
        return

    initials = "".join(
        [p[0].upper() for p in vol["volunteer_name"].split()[:2]]
    ) or "?"

    dept_badge = (
        f"<span class='dept-badge'>{vol['department_name']}</span>"
        if vol["department_name"]
        else "<span class='dept-badge dept-badge-muted'>Not Assigned</span>"
    )

    st.markdown(
        f"""
        <div class="profile-hero">
            <div class="profile-avatar">{initials}</div>
            <div>
                <h2>{vol['volunteer_name']}</h2>
                <p>🏢 {vol['ngo_name']} &nbsp;·&nbsp; {dept_badge}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='section-title'>📋 Personal Information</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Full Name</div>
                <div class="info-value">{vol['volunteer_name']}</div>
                <div class="info-label">Gender</div>
                <div class="info-value">{vol['gender']}</div>
                <div class="info-label">Age</div>
                <div class="info-value">{vol['age'] or '—'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        joining = (
            str(vol["joining_date"])
            if vol["joining_date"]
            else "—"
        )
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Email</div>
                <div class="info-value">{vol['email']}</div>
                <div class="info-label">Phone</div>
                <div class="info-value">{vol['phone'] or '—'}</div>
                <div class="info-label">Joining Date</div>
                <div class="info-value">{joining}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">NGO</div>
                <div class="info-value">{vol['ngo_name']}</div>
                <div class="info-label">Department</div>
                <div class="info-value">{vol['department_name'] or 'Not Assigned'}</div>
                <div class="info-label">Member Since</div>
                <div class="info-value">{vol['created_at']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ── Attendance History ───────────────────────────────────────────────────────

def attendancehistory(vol_id):

    st.markdown(
        "<div class='section-title'>✅ Attendance History</div>",
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
        """,
        (vol_id,)
    )

    # Statistics
    total = len(rows)
    present = sum(
        1
        for r in rows
        if r["attendance_status"] == "Present"
    )

    pct = (
        round((present / total) * 100, 1)
        if total > 0
        else 0
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Events", total)
    c2.metric("Present", present)
    c3.metric("Attendance %", f"{pct}%")

    st.progress(min(int(pct), 100) / 100)

    st.write("")

    if not rows:
        st.info("No attendance records yet.")
        return

    for row in rows:

        is_present = row["attendance_status"] == "Present"
        icon = "✅" if is_present else "❌"
        pill_class = "status-present" if is_present else "status-absent"

        st.markdown(
            f"""
            <div class="attendance-row">
                <div class="attendance-left">
                    <span class="attendance-event">{row['event_name']}</span>
                    <span class="attendance-date">{row['event_date']}</span>
                </div>
                <span class="status-pill {pill_class}">{icon} {row['attendance_status']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='marked-caption'>Marked on: {row['marked_on']}</div>",
            unsafe_allow_html=True,
        )


# ── Upcoming Events ──────────────────────────────────────────────────────────

def upcomingevents(vol_id):

    st.markdown(
        "<div class='section-title'>📅 Upcoming Events</div>",
        unsafe_allow_html=True,
    )

    vol = fetch_one(
        """
        SELECT ngo_id
        FROM volunteers
        WHERE volunteer_id=%s
        """,
        (vol_id,)
    )

    if not vol:
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
                f"<div class='event-meta'>📝 <b>Description:</b> {event['description'] or '—'}</div>",
                unsafe_allow_html=True,
            )