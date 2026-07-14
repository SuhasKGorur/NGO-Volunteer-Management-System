# pages/events.py
# NGO: Create, Read, Update, Delete own events

import streamlit as st
from database import fetch_all, execute_query
from datetime import date


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
        .vol-field-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            color: rgba(120,120,120,0.8);
            margin-bottom: -0.2rem;
        }
        .vol-field-value {
            font-size: 0.95rem;
            margin-bottom: 0.6rem;
        }
        .status-pill {
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 700;
            white-space: nowrap;
        }
        .status-upcoming {
            background: rgba(59,130,246,0.12);
            color: #2563EB;
        }
        .status-completed {
            background: rgba(34,197,94,0.12);
            color: #16A34A;
        }
        .status-cancelled {
            background: rgba(239,68,68,0.12);
            color: #DC2626;
        }
        .form-section-title {
            font-weight: 700;
            font-size: 0.95rem;
            margin: 0.2rem 0 0.6rem 0;
            color: rgba(99,102,241,0.95);
        }
        hr {
            margin: 0.6rem 0 1.2rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def status_pill(status):
    cls_map = {
        "Upcoming": "status-upcoming",
        "Completed": "status-completed",
        "Cancelled": "status-cancelled",
    }
    icon_map = {
        "Upcoming": "🔔",
        "Completed": "✅",
        "Cancelled": "❌",
    }
    cls = cls_map.get(status, "status-upcoming")
    icon = icon_map.get(status, "📅")
    return f"<span class='status-pill {cls}'>{icon} {status}</span>"


def field(col, label, value):
    col.markdown(f"<div class='vol-field-label'>{label}</div>", unsafe_allow_html=True)
    col.markdown(f"<div class='vol-field-value'>{value}</div>", unsafe_allow_html=True)


def show_events():

    inject_css()

    st.markdown(
        """
        <div class="dash-hero">
            <h1>📅 Event Management</h1>
            <p>Create, track and manage the events your organization runs.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(
        ["📋 My Events", "➕ Create Event"]
    )

    with tab1:
        listevents()

    with tab2:
        createevent()


# ── List Events ──────────────────────────────────────────────────────────────

def listevents():

    ngo_id = st.session_state.user_id

    st.markdown(
        "<div class='section-title'>📋 All Events</div>",
        unsafe_allow_html=True,
    )

    fc1, fc2 = st.columns([1, 2])

    status_filter = fc1.selectbox(
        "Filter by Status",
        ["All", "Upcoming", "Completed", "Cancelled"],
        key="event_status_filter"
    )

    search = fc2.text_input(
        "🔍 Search event",
        key="event_search",
        placeholder="Type an event name to filter…",
    )

    query = "SELECT * FROM events WHERE ngo_id=%s"
    params = [ngo_id]

    if status_filter != "All":
        query += " AND event_status=%s"
        params.append(status_filter)

    query += " ORDER BY event_date DESC"

    rows = fetch_all(query, tuple(params))

    if not rows:
        st.info("No events found.")
        return

    upcoming_n = sum(1 for e in rows if e["event_status"] == "Upcoming")
    completed_n = sum(1 for e in rows if e["event_status"] == "Completed")
    cancelled_n = sum(1 for e in rows if e["event_status"] == "Cancelled")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📅 Total", len(rows))
    m2.metric("🔔 Upcoming", upcoming_n)
    m3.metric("✅ Completed", completed_n)
    m4.metric("❌ Cancelled", cancelled_n)

    st.markdown("<hr>", unsafe_allow_html=True)

    filtered = [
        e for e in rows
        if not search or search.lower() in e["event_name"].lower()
    ]

    if not filtered:
        st.warning("No events match your search.")
        return

    for event in filtered:

        with st.expander(
            f"{event['event_name']}  ·  {event['event_date']}"
        ):
            st.markdown(status_pill(event["event_status"]), unsafe_allow_html=True)
            st.write("")

            c1, c2 = st.columns(2)

            field(c1, "Location", event["location"] or "—")
            field(c1, "Date", event["event_date"])

            field(c2, "Status", event["event_status"])
            field(c2, "Created", event["created_at"])

            field(st, "Description", event["description"] or "—")

            st.markdown("<hr>", unsafe_allow_html=True)

            col_e, col_d = st.columns([3, 1])

            with col_e:
                editevent_form(event)

            with col_d:
                st.markdown("**🗑️ Danger Zone**")
                st.caption("This will also remove attendance records.")

                if st.button(
                    "Delete Event",
                    key=f"del_ev_{event['event_id']}",
                    use_container_width=True,
                    type="secondary",
                ):
                    deleteevent(event["event_id"])


def editevent_form(event):
    """Inline edit form for an event."""

    status_options = [
        "Upcoming",
        "Completed",
        "Cancelled"
    ]

    with st.form(f"edit_ev_{event['event_id']}"):

        st.markdown("**✏️ Edit Event**")

        name = st.text_input(
            "Event Name",
            value=event["event_name"]
        )

        dc, sc = st.columns(2)

        ev_date = dc.date_input(
            "Event Date",
            value=event["event_date"] if event["event_date"] else date.today()
        )

        status = sc.selectbox(
            "Status",
            status_options,
            index=status_options.index(event["event_status"])
        )

        location = st.text_input(
            "Location",
            value=event["location"] or ""
        )

        desc = st.text_area(
            "Description",
            value=event["description"] or ""
        )

        save = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if save:

            if not name.strip():
                st.error("Event name is required.")
                return

            ok = execute_query(
                """
                UPDATE events
                SET
                    event_name=%s,
                    event_date=%s,
                    location=%s,
                    description=%s,
                    event_status=%s
                WHERE event_id=%s
                """,
                (
                    name,
                    ev_date.strftime("%Y-%m-%d"),
                    location,
                    desc,
                    status,
                    event["event_id"]
                )
            )

            if ok:
                st.success("Event updated!")
                st.rerun()
            else:
                st.error("Update failed.")


def deleteevent(event_id):

    ok = execute_query(
        "DELETE FROM events WHERE event_id=%s",
        (event_id,)
    )

    if ok:
        st.success("Event deleted.")
        st.rerun()
    else:
        st.error("Delete failed.")


# ── Create Event ─────────────────────────────────────────────────────────────

def createevent():

    ngo_id = st.session_state.user_id

    st.markdown("### ➕ Create New Event")
    st.caption("Fields marked with * are required.")

    with st.form("create_event_form"):

        st.markdown(
            "<div class='form-section-title'>📋 Event Details</div>",
            unsafe_allow_html=True,
        )

        name = st.text_input("Event Name *", placeholder="e.g. Beach Cleanup Drive")

        dc, sc = st.columns(2)

        ev_date = dc.date_input(
            "Event Date",
            value=date.today()
        )

        status = sc.selectbox(
            "Status",
            ["Upcoming", "Completed", "Cancelled"]
        )

        location = st.text_input("Location", placeholder="Optional")
        desc = st.text_area("Description", placeholder="Optional")

        st.write("")
        submit = st.form_submit_button(
            "✅ Create Event",
            use_container_width=True,
            type="primary",
        )

        if submit:

            if not name.strip():
                st.warning("Event name is required.")
                return

            ok = execute_query(
                """
                INSERT INTO events
                (
                    ngo_id,
                    event_name,
                    event_date,
                    location,
                    description,
                    event_status
                )
                VALUES
                (%s, %s, %s, %s, %s, %s)
                """,
                (
                    ngo_id,
                    name,
                    ev_date.strftime("%Y-%m-%d"),
                    location,
                    desc,
                    status
                )
            )

            if ok:
                st.success(
                    f"Event '{name}' created successfully!"
                )
                st.rerun()
            else:
                st.error("Failed to create event.")