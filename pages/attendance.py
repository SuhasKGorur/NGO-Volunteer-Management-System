# pages/attendance.py
# NGO: Mark and view attendance for own events and volunteers

import streamlit as st
from database import fetch_all, fetch_one, execute_query


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
        .att-selected {
            font-size: 0.9rem;
            border: 1px solid rgba(99,102,241,0.2);
            background: rgba(99,102,241,0.06);
            border-radius: 10px;
            padding: 0.5rem 0.85rem;
            margin-bottom: 1rem;
        }
        .vol-row {
            border: 1px solid rgba(120,120,120,0.15);
            border-radius: 12px;
            padding: 0.65rem 0.9rem;
            margin-bottom: 0.5rem;
        }
        .vol-row-name {
            font-weight: 600;
            font-size: 0.95rem;
        }
        .vol-row-dept {
            font-size: 0.78rem;
            color: rgba(120,120,120,0.85);
        }
        .status-pill {
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            white-space: nowrap;
            display: inline-block;
            margin-top: 4px;
        }
        .status-present {
            background: rgba(34,197,94,0.12);
            color: #16A34A;
        }
        .status-absent {
            background: rgba(239,68,68,0.12);
            color: #DC2626;
        }
        .status-unmarked {
            background: rgba(120,120,120,0.12);
            color: rgba(120,120,120,0.9);
        }
        hr {
            margin: 0.6rem 0 1.2rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_pill(current):
    if current == "Present":
        return "<span class='status-pill status-present'>✅ Present</span>"
    elif current == "Absent":
        return "<span class='status-pill status-absent'>❌ Absent</span>"
    else:
        return "<span class='status-pill status-unmarked'>⏳ Not Marked</span>"


def show_attendance():

    inject_css()

    st.markdown(
        """
        <div class="dash-hero">
            <h1>✅ Attendance Management</h1>
            <p>Mark attendance for your events and review participation reports.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(
        ["📝 Mark Attendance", "📊 Attendance Report"]
    )

    with tab1:
        markattendance()

    with tab2:
        attendancereport()


# ── Mark Attendance ──────────────────────────────────────────────────────────

def markattendance():

    ngo_id = st.session_state.user_id

    st.markdown(
        "<div class='section-title'>📝 Mark Attendance</div>",
        unsafe_allow_html=True,
    )

    # Step 1: Select event
    events = fetch_all(
        """
        SELECT
            event_id,
            event_name,
            event_date
        FROM events
        WHERE ngo_id=%s
        ORDER BY event_date DESC
        """,
        (ngo_id,)
    )

    if not events:
        st.info("No events found. Create an event first.")
        return

    event_map = {
        f"{e['event_name']} ({e['event_date']})": e["event_id"]
        for e in events
    }

    selected_event_label = st.selectbox(
        "Select Event",
        list(event_map.keys())
    )

    event_id = event_map[selected_event_label]

    # Step 2: Fetch volunteers for this NGO
    volunteers = fetch_all(
        """
        SELECT
            v.volunteer_id,
            v.volunteer_name,
            d.department_name
        FROM volunteers v
        LEFT JOIN departments d
            ON v.department_id = d.department_id
        WHERE v.ngo_id=%s
        ORDER BY v.volunteer_name
        """,
        (ngo_id,)
    )

    if not volunteers:
        st.info("No volunteers found. Add volunteers first.")
        return

    st.markdown(
        f"<div class='att-selected'>📌 Marking attendance for: <b>{selected_event_label}</b></div>",
        unsafe_allow_html=True,
    )

    # Step 3: For each volunteer show current status and allow update
    for vol in volunteers:

        existing = fetch_one(
            """
            SELECT
                attendance_id,
                attendance_status
            FROM attendance
            WHERE volunteer_id=%s
              AND event_id=%s
            """,
            (
                vol["volunteer_id"],
                event_id
            )
        )

        current = (
            existing["attendance_status"]
            if existing
            else "Not Marked"
        )

        st.markdown("<div class='vol-row'>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([3, 2, 2])

        col1.markdown(
            f"""
            <div class="vol-row-name">🙋 {vol['volunteer_name']}</div>
            <div class="vol-row-dept">{vol['department_name'] or 'No Dept'}</div>
            """,
            unsafe_allow_html=True,
        )

        col2.markdown(status_pill(current), unsafe_allow_html=True)

        options = ["Present", "Absent"]
        default_index = 0 if current == "Present" else 1

        new_status = col3.selectbox(
            "Mark",
            options,
            index=default_index,
            key=f"att_{vol['volunteer_id']}_{event_id}"
        )

        if existing:

            if col3.button(
                "💾 Update",
                key=f"upd_{vol['volunteer_id']}_{event_id}",
                use_container_width=True,
            ):

                ok = execute_query(
                    """
                    UPDATE attendance
                    SET attendance_status=%s
                    WHERE attendance_id=%s
                    """,
                    (
                        new_status,
                        existing["attendance_id"]
                    )
                )

                if ok:
                    st.success(
                        f"Updated {vol['volunteer_name']}"
                    )
                    st.rerun()

        else:

            if col3.button(
                "✅ Save",
                key=f"sav_{vol['volunteer_id']}_{event_id}",
                use_container_width=True,
            ):

                ok = execute_query(
                    """
                    INSERT INTO attendance
                    (
                        volunteer_id,
                        event_id,
                        attendance_status
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        vol["volunteer_id"],
                        event_id,
                        new_status
                    )
                )

                if ok:
                    st.success(
                        f"Marked {vol['volunteer_name']} as {new_status}"
                    )
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ── Attendance Report ────────────────────────────────────────────────────────

def attendancereport():

    ngo_id = st.session_state.user_id

    st.markdown(
        "<div class='section-title'>📊 Attendance Report</div>",
        unsafe_allow_html=True,
    )

    # Summary by event
    st.markdown(
        "<div class='section-title' style='font-size:0.95rem;'>📅 By Event</div>",
        unsafe_allow_html=True,
    )

    event_rows = fetch_all(
        """
        SELECT
            e.event_name,
            e.event_date,
            COUNT(a.attendance_id) AS total,
            SUM(a.attendance_status='Present') AS present,
            SUM(a.attendance_status='Absent') AS absent
        FROM events e
        LEFT JOIN attendance a
            ON a.event_id = e.event_id
        WHERE e.ngo_id=%s
        GROUP BY e.event_id
        ORDER BY e.event_date DESC
        """,
        (ngo_id,)
    )

    if not event_rows:
        st.info("No events or attendance data available.")

    else:

        for row in event_rows:

            with st.expander(
                f"📅 {row['event_name']}  ·  {row['event_date']}"
            ):

                c1, c2, c3 = st.columns(3)

                c1.metric("Total Marked", row["total"])
                c2.metric("✅ Present", row["present"] or 0)
                c3.metric("❌ Absent", row["absent"] or 0)

                total = row["total"] or 0
                present = row["present"] or 0
                pct = round((present / total) * 100, 1) if total > 0 else 0

                st.progress(min(int(pct), 100) / 100)
                st.caption(f"{pct}% attendance for this event")

    st.markdown("<hr>", unsafe_allow_html=True)

    # Summary by volunteer
    st.markdown(
        "<div class='section-title' style='font-size:0.95rem;'>🙋 By Volunteer</div>",
        unsafe_allow_html=True,
    )

    vol_rows = fetch_all(
        """
        SELECT
            v.volunteer_name,
            COUNT(a.attendance_id) AS total,
            SUM(a.attendance_status='Present') AS present,
            SUM(a.attendance_status='Absent') AS absent
        FROM volunteers v
        LEFT JOIN attendance a
            ON a.volunteer_id = v.volunteer_id
        WHERE v.ngo_id=%s
        GROUP BY v.volunteer_id
        ORDER BY v.volunteer_name
        """,
        (ngo_id,)
    )

    if not vol_rows:
        st.info("No volunteer attendance data available.")

    else:

        for row in vol_rows:

            total = row["total"] or 0
            present = row["present"] or 0

            pct = (
                round((present / total) * 100, 1)
                if total > 0
                else 0
            )

            with st.expander(
                f"🙋 {row['volunteer_name']}  ·  {pct}% attendance"
            ):

                c1, c2, c3, c4 = st.columns(4)

                c1.metric("Events", total)
                c2.metric("✅ Present", present)
                c3.metric("❌ Absent", row["absent"] or 0)
                c4.metric("📈 %", f"{pct}%")

                st.progress(min(int(pct), 100) / 100)