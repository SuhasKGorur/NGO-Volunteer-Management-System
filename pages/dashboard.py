"""
====================================================
Department Management
====================================================
"""

import streamlit as st

from database import (
    fetch_all,
    fetch_one,
    execute_query
)


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
        .dept-card {
            border: 1px solid rgba(120,120,120,0.15);
            border-radius: 14px;
            padding: 1.1rem 1.3rem;
            margin-bottom: 1rem;
        }
        .dept-card h4 {
            margin: 0 0 0.4rem 0;
            font-size: 1.15rem;
        }
        .dept-desc {
            font-size: 0.9rem;
            color: rgba(90,90,90,0.95);
            line-height: 1.45;
        }
        .form-section-title {
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin: 0.2rem 0 0.5rem 0;
            color: rgba(99,102,241,0.95);
        }
        hr {
            margin: 0.8rem 0 1.2rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def department_management():

    inject_css()

    st.markdown(
        """
        <div class="dash-hero">
            <h1>🏢 Department Management</h1>
            <p>Manage NGO departments — create, search, edit and remove.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------
    # Add Department
    # -----------------------------

    with st.expander("➕ Add Department", expanded=True):

        st.markdown(
            "<div class='form-section-title'>New Department</div>",
            unsafe_allow_html=True,
        )

        department_name = st.text_input(
            "Department Name",
            placeholder="e.g. Fundraising"
        )

        description = st.text_area(
            "Description",
            placeholder="What does this department do?"
        )

        if st.button(
            "✅ Add Department",
            use_container_width=True,
            type="primary",
        ):

            if department_name == "":

                st.warning(
                    "Department Name is required."
                )

            else:

                check_query = """
                SELECT *
                FROM departments
                WHERE department_name=%s
                """

                department = fetch_one(
                    check_query,
                    (department_name,)
                )

                if department:

                    st.error(
                        "Department already exists."
                    )

                else:

                    insert_query = """
                    INSERT INTO departments
                    (
                        department_name,
                        description
                    )
                    VALUES
                    (
                        %s,%s
                    )
                    """

                    values = (
                        department_name,
                        description
                    )

                    if execute_query(
                        insert_query,
                        values
                    ):

                        st.success(
                            "Department Added Successfully."
                        )

                        st.rerun()

    st.write("")

    # -----------------------------
    # Search Department
    # -----------------------------

    search = st.text_input(
        "🔍 Search Department",
        placeholder="Type a department name to filter…",
    )

    if search == "":

        query = """
        SELECT *
        FROM departments
        ORDER BY department_name
        """

        departments = fetch_all(query)

    else:

        query = """
        SELECT *
        FROM departments
        WHERE department_name LIKE %s
        ORDER BY department_name
        """

        departments = fetch_all(
            query,
            ("%" + search + "%",)
        )

    st.markdown(
        "<div class='section-title'>📋 Department List</div>",
        unsafe_allow_html=True,
    )

    if departments:

        for department in departments:

            with st.container():

                st.markdown("<div class='dept-card'>", unsafe_allow_html=True)

                col1, col2 = st.columns([3, 2])

                with col1:

                    st.markdown(
                        f"""
                        <h4>🏛️ {department['department_name']}</h4>
                        <div class="dept-desc">{department['description'] or 'No description provided.'}</div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col2:

                    st.markdown(
                        "<div class='form-section-title'>✏️ Edit</div>",
                        unsafe_allow_html=True,
                    )

                    new_name = st.text_input(
                        "Department Name",
                        value=department["department_name"],
                        key=f"name{department['department_id']}"
                    )

                    new_description = st.text_area(
                        "Description",
                        value=department["description"],
                        key=f"desc{department['department_id']}"
                    )

                    bc1, bc2 = st.columns(2)

                    with bc1:
                        if st.button(
                            "💾 Update",
                            key=f"update{department['department_id']}",
                            use_container_width=True,
                        ):

                            update_query = """
                            UPDATE departments
                            SET
                            department_name=%s,
                            description=%s
                            WHERE department_id=%s
                            """

                            values = (

                                new_name,

                                new_description,

                                department["department_id"]

                            )

                            if execute_query(
                                update_query,
                                values
                            ):

                                st.success(
                                    "Department Updated Successfully."
                                )

                                st.rerun()

                    with bc2:
                        if st.button(
                            "🗑️ Delete",
                            key=f"delete{department['department_id']}",
                            type="secondary",
                            use_container_width=True,
                        ):

                            # Check whether department is assigned to volunteers
                            check_query = """
                            SELECT COUNT(*) AS total
                            FROM volunteers
                            WHERE department_id=%s
                            """

                            result = fetch_one(
                                check_query,
                                (department["department_id"],)
                            )

                            if result["total"] > 0:

                                st.error(
                                    "Cannot delete. Volunteers are assigned to this department."
                                )

                            else:

                                delete_query = """
                                DELETE FROM departments
                                WHERE department_id=%s
                                """

                                if execute_query(
                                    delete_query,
                                    (department["department_id"],)
                                ):

                                    st.success(
                                        "Department Deleted Successfully."
                                    )

                                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    else:

        st.info("No Departments Found.")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.caption(
        f"Total Departments : {len(departments)}"
    )