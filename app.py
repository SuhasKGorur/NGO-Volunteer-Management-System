import streamlit as st

st.set_page_config(
    page_title="NGO Volunteer System",
    layout="wide"
)

st.title("NGO Volunteer Management System")

st.write("Welcome to our NGO Dashboard")
with st.container():
    st.subheader("About NGO")

    st.write("""Our NGO helps:
                -Volunteers
                -Animals
                -Environment
            """)

menu=st.sidebar.selectbox(
    "Navigation",["Dashboard","Volunteers","Events"]
)

#Dashboard Page
if menu == "Dashboard":
    st.header("Dashboard")

    col1,col2,col3 = st.columns(3)

    col1.metric("Volunteers",120)
    col2.metric("Events",15)
    col3.metric("Attendance","89%")

#Volunteers page

elif menu == "Volunteers":

    st.header("Volunteer Registration")

    name = st.text_input("Volunteer Name")

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100
    )

    department = st.selectbox(
        "Department",
        ["Environment", "Animal Welfare", "Education"]
    )

    gender = st.radio(
        "Gender",
        ["Male", "Female", "Other"]
    )

    available = st.checkbox(
        "Available for Weekend Activities"
    )

    if st.button("Register Volunteer"):

        st.success("Volunteer Registered Successfully")

        st.write("Name:", name)
        st.write("Age:", age)
        st.write("Department:", department)
        st.write("Gender:", gender)
        st.write("Weekend Availability:", available)

# EVENTS PAGE
elif menu == "Events":

    st.header("Event Management")

