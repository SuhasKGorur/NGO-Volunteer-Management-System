import streamlit as st

from database import (
    fetch_one,
    execute_query
)


def inject_css():
    st.markdown(
        """
        <style>
        .reg-hero {
            background: linear-gradient(135deg, rgba(99,102,241,0.10), rgba(99,102,241,0.02));
            border: 1px solid rgba(99,102,241,0.15);
            border-radius: 18px;
            padding: 1.3rem 1.6rem;
            margin-bottom: 1.4rem;
        }
        .reg-hero h2 {
            margin: 0 0 0.15rem 0;
            font-size: 1.5rem;
        }
        .reg-hero p {
            margin: 0;
            color: rgba(120,120,120,0.9);
            font-size: 0.92rem;
        }
        div[data-testid="stForm"] {
            border: 1px solid rgba(120,120,120,0.15);
            border-radius: 16px;
            padding: 1.4rem 1.6rem 1rem 1.6rem;
        }
        .form-section-title {
            font-weight: 700;
            font-size: 0.95rem;
            margin: 0.2rem 0 0.6rem 0;
            color: rgba(99,102,241,0.95);
        }
        .required-hint {
            font-size: 0.78rem;
            color: rgba(120,120,120,0.75);
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------
# NGO Registration Form
# ---------------------------------------------
def ngo_registration():

    inject_css()

    st.markdown(
        """
        <div class="reg-hero">
            <h2>🏢 NGO Registration</h2>
            <p>Register your organization to start managing volunteers, events and attendance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("ngo_registration_form"):

        st.markdown(
            "<div class='form-section-title'>📋 Organization Details</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='required-hint'>Fields marked * are required.</div>",
            unsafe_allow_html=True,
        )

        ngo_name = st.text_input("NGO Name *", placeholder="e.g. Green Earth Foundation")

        c1, c2 = st.columns(2)
        reg_no = c1.text_input("Registration Number", placeholder="Optional")
        phone = c2.text_input("Phone Number", placeholder="Optional")

        address = st.text_area("Address", placeholder="Street, City, State, PIN")

        st.markdown(
            "<div class='form-section-title'>🔐 Account Credentials</div>",
            unsafe_allow_html=True,
        )

        email = st.text_input("Email *", placeholder="contact@ngo.org")

        c3, c4 = st.columns(2)
        password = c3.text_input(
            "Password *",
            type="password"
        )
        confirm = c4.text_input(
            "Confirm Password *",
            type="password"
        )

        st.write("")

        submitted = st.form_submit_button(
            "✅ Register NGO",
            use_container_width=True,
            type="primary",
        )

        if submitted:

            if ngo_name == "" or email == "" or password == "":

                st.error("Please fill all required fields.")

                return

            if password != confirm:

                st.error("Passwords do not match.")

                return

            check_query = """
            SELECT *
            FROM ngos
            WHERE email=%s
            """

            ngo = fetch_one(
                check_query,
                (email,)
            )

            if ngo:

                st.error("Email already exists.")

                return

            insert_query = """
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
            (
                %s,%s,%s,%s,%s,%s
            )
            """

            values = (
                ngo_name,
                reg_no,
                email,
                phone,
                address,
                password
            )

            if execute_query(
                insert_query,
                values
            ):

                st.success(
                    "Registration Successful.\n\nWait for Admin Approval."
                )