# pages/departments.py
# Admin-only: Create, Read, Update, Delete departments

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
        .desc-box {
            font-size: 0.92rem;
            color: rgba(60,60,60,0.95);
            border: 1px solid rgba(120,120,120,0.15);
            border-radius: 10px;
            padding: 0.6rem 0.85rem;
            margin-bottom: 0.9rem;
            background: rgba(120,120,120,0.03);
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


def show_departments():

    inject_css()

    st.markdown(
        """
        <div class="dash-hero">
            <h1>🏛️ Department Management</h1>
            <p>Organize volunteers into departments across the platform.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(
        ["📋 All Departments", "➕ Add Department"]
    )

    with tab1:
        listdepartments()

    with tab2:
        adddepartment()


# ── List + Edit + Delete ─────────────────────────────────────────────────────

def listdepartments():

    st.markdown(
        "<div class='section-title'>📋 All Departments</div>",
        unsafe_allow_html=True,
    )

    rows = fetch_all(
        """
        SELECT
            d.department_id,
            d.department_name,
            d.description,
            COUNT(v.volunteer_id) AS vol_count
        FROM departments d
        LEFT JOIN volunteers v
            ON v.department_id = d.department_id
        GROUP BY d.department_id
        ORDER BY d.department_name
        """
    )

    if not rows:
        st.info("No departments found. Add one using the tab above.")
        return

    total_depts = len(rows)
    total_vols = sum(d["vol_count"] for d in rows)
    empty_depts = sum(1 for d in rows if d["vol_count"] == 0)

    m1, m2, m3 = st.columns(3)
    m1.metric("🏛️ Total Departments", total_depts)
    m2.metric("👥 Volunteers Assigned", total_vols)
    m3.metric("📭 Empty Departments", empty_depts)

    st.write("")

    search = st.text_input(
        "🔍 Search department",
        key="dept_search",
        placeholder="Type a department name to filter…",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    filtered = [
        d for d in rows
        if not search or search.lower() in d["department_name"].lower()
    ]

    if not filtered:
        st.warning("No departments match your search.")
        return

    for dept in filtered:

        vol_badge = (
            f"<span class='vol-badge'>{dept['vol_count']} volunteer(s)</span>"
            if dept["vol_count"] > 0
            else "<span class='vol-badge vol-badge-muted'>No volunteers</span>"
        )

        with st.expander(f"🏛️ {dept['department_name']}"):

            st.markdown(vol_badge, unsafe_allow_html=True)
            st.write("")

            st.markdown(
                f"<div class='desc-box'>{dept['description'] or 'No description provided.'}</div>",
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)

            # ── Edit Form ───────────────────────────────────────────────

            with col1:

                with st.form(f"edit_dept_{dept['department_id']}"):

                    st.markdown("**✏️ Edit Department**")

                    new_name = st.text_input(
                        "Name",
                        value=dept["department_name"],
                        key=f"dn_{dept['department_id']}"
                    )

                    new_desc = st.text_area(
                        "Description",
                        value=dept["description"] or "",
                        key=f"dd_{dept['department_id']}"
                    )

                    save = st.form_submit_button(
                        "💾 Save Changes",
                        use_container_width=True,
                    )

                    if save:
                        updatedepartment(
                            dept["department_id"],
                            new_name,
                            new_desc
                        )

            # ── Delete Section ──────────────────────────────────────────

            with col2:

                st.markdown("**🗑️ Danger Zone**")

                if dept["vol_count"] > 0:

                    st.warning(
                        f"Cannot delete — {dept['vol_count']} volunteer(s) assigned."
                    )

                else:

                    st.caption("This action cannot be undone.")

                    if st.button(
                        "Delete Department",
                        key=f"del_dept_{dept['department_id']}",
                        use_container_width=True,
                        type="secondary",
                    ):
                        deletedepartment(dept["department_id"])


def updatedepartment(dept_id, name, description):

    if not name.strip():
        st.error("Department name cannot be empty.")
        return

    # Check name collision (excluding current department)
    existing = fetch_one(
        """
        SELECT department_id
        FROM departments
        WHERE department_name=%s
          AND department_id!=%s
        """,
        (name.strip(), dept_id)
    )

    if existing:
        st.error("Another department with this name already exists.")
        return

    ok = execute_query(
        """
        UPDATE departments
        SET department_name=%s,
            description=%s
        WHERE department_id=%s
        """,
        (
            name.strip(),
            description.strip(),
            dept_id
        )
    )

    if ok:
        st.success("Department updated!")
        st.rerun()

    else:
        st.error("Update failed.")


def deletedepartment(dept_id):

    ok = execute_query(
        "DELETE FROM departments WHERE department_id=%s",
        (dept_id,)
    )

    if ok:
        st.success("Department deleted.")
        st.rerun()

    else:
        st.error("Delete failed.")


# ── Add Department ───────────────────────────────────────────────────────────

def adddepartment():

    st.markdown("### ➕ Add New Department")
    st.caption("Fields marked with * are required.")

    with st.form("add_dept_form"):

        st.markdown(
            "<div class='form-section-title'>🏛️ Department Details</div>",
            unsafe_allow_html=True,
        )

        name = st.text_input("Department Name *", placeholder="e.g. Fundraising")
        desc = st.text_area("Description", placeholder="Optional — what does this department do?")

        st.write("")
        submitted = st.form_submit_button(
            "✅ Add Department",
            use_container_width=True,
            type="primary",
        )

        if submitted:

            if not name.strip():
                st.warning("Department name is required.")
                return

            existing = fetch_one(
                """
                SELECT department_id
                FROM departments
                WHERE department_name=%s
                """,
                (name.strip(),)
            )

            if existing:
                st.error("A department with this name already exists.")
                return

            ok = execute_query(
                """
                INSERT INTO departments
                (department_name, description)
                VALUES (%s, %s)
                """,
                (
                    name.strip(),
                    desc.strip()
                )
            )

            if ok:
                st.success(
                    f"Department '{name}' added successfully!"
                )
                st.rerun()

            else:
                st.error("Failed to add department.")