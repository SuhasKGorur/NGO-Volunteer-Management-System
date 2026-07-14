# pages/volunteers.py
# NGO: manage own volunteers | Admin: view all volunteers

import streamlit as st
from database import fetch_all, fetch_one, execute_query
from datetime import date


# ── Shared styling ───────────────────────────────────────────────────────────

def inject_css():
    st.markdown(
        """
        <style>
        .vol-header {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 0.25rem;
        }
        .vol-subtitle {
            color: rgba(120,120,120,0.9);
            font-size: 0.95rem;
            margin-bottom: 1.2rem;
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
            font-size: 1.02rem;
        }
        .vol-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            background: rgba(99,102,241,0.12);
            color: #6366F1;
            margin-left: 6px;
        }
        .vol-badge-muted {
            background: rgba(120,120,120,0.12);
            color: rgba(120,120,120,0.9);
        }
        .vol-field-label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            color: rgba(120,120,120,0.8);
            margin-bottom: -0.2rem;
        }
        .vol-field-value {
            font-size: 0.95rem;
            margin-bottom: 0.6rem;
        }
        hr {
            margin: 0.6rem 0 1.2rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def field(col, label, value):
    col.markdown(f"<div class='vol-field-label'>{label}</div>", unsafe_allow_html=True)
    col.markdown(f"<div class='vol-field-value'>{value}</div>", unsafe_allow_html=True)


def show_volunteers():

    role = st.session_state.role

    inject_css()

    st.markdown(
        "<div class='vol-header'><h1 style='margin:0;'>👥 Volunteer Management</h1></div>",
        unsafe_allow_html=True,
    )

    if role == "admin":
        st.markdown(
            "<div class='vol-subtitle'>A unified view of every volunteer across all partner NGOs.</div>",
            unsafe_allow_html=True,
        )
        adminview()
    else:
        st.markdown(
            "<div class='vol-subtitle'>Manage the volunteers registered under your organization.</div>",
            unsafe_allow_html=True,
        )
        tab1, tab2 = st.tabs(
            ["📋 My Volunteers", "➕ Add Volunteer"]
        )

        with tab1:
            listvolunteers()

        with tab2:
            addvolunteer()


# ── Admin View ───────────────────────────────────────────────────────────────

def adminview():

    rows = fetch_all(
        """
        SELECT
            v.volunteer_id,
            v.volunteer_name,
            v.gender,
            v.age,
            v.email,
            v.phone,
            v.joining_date,
            d.department_name,
            n.ngo_name
        FROM volunteers v
        LEFT JOIN departments d
            ON v.department_id = d.department_id
        INNER JOIN ngos n
            ON v.ngo_id = n.ngo_id
        ORDER BY n.ngo_name, v.volunteer_name
        """
    )

    if not rows:
        st.info("No volunteers in the system.")
        return

    total_volunteers = len(rows)
    total_ngos = len({r["ngo_name"] for r in rows})
    total_depts = len({r["department_name"] for r in rows if r["department_name"]})

    m1, m2, m3 = st.columns(3)
    m1.metric("👤 Total Volunteers", total_volunteers)
    m2.metric("🏢 NGOs", total_ngos)
    m3.metric("🗂️ Departments Covered", total_depts)

    st.write("")

    search = st.text_input(
        "🔍 Search volunteer by name",
        key="admin_vol_search",
        placeholder="Type a name to filter…",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    filtered = [
        v for v in rows
        if not search or search.lower() in v["volunteer_name"].lower()
    ]

    if not filtered:
        st.warning("No volunteers match your search.")
        return

    for v in filtered:

        dept_badge = (
            f"<span class='vol-badge'>{v['department_name']}</span>"
            if v["department_name"]
            else "<span class='vol-badge vol-badge-muted'>No Dept</span>"
        )

        with st.expander(
            f"🙋 {v['volunteer_name']}  ·  🏢 {v['ngo_name']}"
        ):
            st.markdown(dept_badge, unsafe_allow_html=True)
            st.write("")

            c1, c2 = st.columns(2)

            field(c1, "Gender", v["gender"])
            field(c1, "Age", v["age"] or "—")
            field(c1, "Email", v["email"])

            field(c2, "Phone", v["phone"] or "—")
            field(c2, "Joined", v["joining_date"] or "—")


# ── NGO: List own volunteers ────────────────────────────────────────────────

def listvolunteers():

    ngo_id = st.session_state.user_id

    rows = fetch_all(
        """
        SELECT
            v.volunteer_id,
            v.volunteer_name,
            v.gender,
            v.age,
            v.email,
            v.phone,
            v.joining_date,
            d.department_name
        FROM volunteers v
        LEFT JOIN departments d
            ON v.department_id = d.department_id
        WHERE v.ngo_id=%s
        ORDER BY v.volunteer_name
        """,
        (ngo_id,)
    )

    if not rows:
        st.info("No volunteers yet. Add one using the **➕ Add Volunteer** tab.")
        return

    total_volunteers = len(rows)
    total_depts = len({r["department_name"] for r in rows if r["department_name"]})
    no_dept = sum(1 for r in rows if not r["department_name"])

    m1, m2, m3 = st.columns(3)
    m1.metric("👤 Total Volunteers", total_volunteers)
    m2.metric("🗂️ Departments", total_depts)
    m3.metric("❔ Unassigned", no_dept)

    st.write("")

    search = st.text_input(
        "🔍 Search volunteer by name",
        key="ngo_vol_search",
        placeholder="Type a name to filter…",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    filtered = [
        v for v in rows
        if not search or search.lower() in v["volunteer_name"].lower()
    ]

    if not filtered:
        st.warning("No volunteers match your search.")
        return

    for v in filtered:

        dept_badge = (
            f"<span class='vol-badge'>{v['department_name']}</span>"
            if v["department_name"]
            else "<span class='vol-badge vol-badge-muted'>No Dept</span>"
        )

        with st.expander(
            f"🙋 {v['volunteer_name']}"
        ):
            st.markdown(dept_badge, unsafe_allow_html=True)
            st.write("")

            c1, c2 = st.columns(2)

            field(c1, "Gender", v["gender"])
            field(c1, "Age", v["age"] or "—")
            field(c1, "Email", v["email"])

            field(c2, "Phone", v["phone"] or "—")
            field(c2, "Joined", v["joining_date"] or "—")

            st.markdown("<hr>", unsafe_allow_html=True)

            col_e, col_d = st.columns([3, 1])

            with col_e:
                editvolunteer_form(v)

            with col_d:
                st.markdown("**🗑️ Danger Zone**")
                st.caption("This action cannot be undone.")

                if st.button(
                    "Delete Volunteer",
                    key=f"del_vol_{v['volunteer_id']}",
                    use_container_width=True,
                    type="secondary",
                ):
                    deletevolunteer(v["volunteer_id"])


def editvolunteer_form(v):
    """Inline edit form for a volunteer record."""

    departments = fetch_all(
        """
        SELECT department_id, department_name
        FROM departments
        ORDER BY department_name
        """
    )

    dept_map = {
        d["department_name"]: d["department_id"]
        for d in departments
    }

    dept_names = ["— None —"] + list(dept_map.keys())

    # Pre-select current department
    current_dept = v["department_name"] or "— None —"

    if current_dept not in dept_names:
        current_dept = "— None —"

    with st.form(f"edit_vol_{v['volunteer_id']}"):

        st.markdown("**✏️ Edit Volunteer**")

        name = st.text_input(
            "Name",
            value=v["volunteer_name"]
        )

        gc, ac = st.columns(2)

        gender = gc.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            index=["Male", "Female", "Other"].index(v["gender"])
        )

        age = ac.number_input(
            "Age",
            min_value=10,
            max_value=100,
            value=int(v["age"]) if v["age"] else 18
        )

        phone = st.text_input(
            "Phone",
            value=v["phone"] or ""
        )

        dept = st.selectbox(
            "Department",
            dept_names,
            index=dept_names.index(current_dept)
        )

        save = st.form_submit_button("💾 Save Changes", use_container_width=True)

        if save:

            dept_id = (
                dept_map.get(dept)
                if dept != "— None —"
                else None
            )

            ok = execute_query(
                """
                UPDATE volunteers
                SET
                    volunteer_name=%s,
                    gender=%s,
                    age=%s,
                    phone=%s,
                    department_id=%s
                WHERE volunteer_id=%s
                """,
                (
                    name,
                    gender,
                    age,
                    phone,
                    dept_id,
                    v["volunteer_id"]
                )
            )

            if ok:
                st.success("Updated!")
                st.rerun()
            else:
                st.error("Update failed.")


def deletevolunteer(vol_id):

    ok = execute_query(
        "DELETE FROM volunteers WHERE volunteer_id=%s",
        (vol_id,)
    )

    if ok:
        st.success("Volunteer removed.")
        st.rerun()
    else:
        st.error("Delete failed.")


# ── Add Volunteer ────────────────────────────────────────────────────────────

def addvolunteer():

    ngo_id = st.session_state.user_id

    st.markdown("### ➕ Add New Volunteer")
    st.caption("Fields marked with * are required.")

    departments = fetch_all(
        """
        SELECT department_id, department_name
        FROM departments
        ORDER BY department_name
        """
    )

    dept_map = {
        d["department_name"]: d["department_id"]
        for d in departments
    }

    dept_names = ["— None —"] + list(dept_map.keys())

    with st.form("add_vol_form"):

        st.markdown("##### 👤 Basic Details")
        name = st.text_input("Full Name *", placeholder="e.g. Priya Sharma")

        cc1, cc2 = st.columns(2)
        email = cc1.text_input("Email *", placeholder="name@example.com")
        password = cc2.text_input("Password *", type="password")

        st.markdown("##### ℹ️ Profile Info")
        gc, ac = st.columns(2)

        gender = gc.selectbox(
            "Gender",
            ["Male", "Female", "Other"]
        )

        age = ac.number_input(
            "Age",
            min_value=10,
            max_value=100,
            value=20
        )

        phone = st.text_input("Phone", placeholder="Optional")

        st.markdown("##### 🗂️ Assignment")
        dc, jc = st.columns(2)

        dept = dc.selectbox(
            "Department",
            dept_names
        )

        joining = jc.date_input(
            "Joining Date",
            value=date.today()
        )

        st.write("")
        submit = st.form_submit_button(
            "✅ Add Volunteer",
            use_container_width=True,
            type="primary",
        )

        if submit:

            if not all([name, email, password]):
                st.warning(
                    "Name, Email and Password are required."
                )
                return

            existing = fetch_one(
                """
                SELECT volunteer_id
                FROM volunteers
                WHERE email=%s
                """,
                (email,)
            )

            if existing:
                st.error(
                    "A volunteer with this email already exists."
                )
                return

            dept_id = (
                dept_map.get(dept)
                if dept != "— None —"
                else None
            )

            ok = execute_query(
                """
                INSERT INTO volunteers
                (
                    ngo_id,
                    department_id,
                    volunteer_name,
                    gender,
                    age,
                    phone,
                    email,
                    password,
                    joining_date
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    ngo_id,
                    dept_id,
                    name,
                    gender,
                    age,
                    phone,
                    email,
                    password,
                    joining.strftime("%Y-%m-%d")
                )
            )

            if ok:
                st.success(
                    f"Volunteer '{name}' added successfully!"
                )
                st.rerun()
            else:
                st.error("Failed to add volunteer.")