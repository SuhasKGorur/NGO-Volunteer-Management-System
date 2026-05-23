import streamlit as st

st.title("NGO Volunteer Management System")
st.write("Welcome to our NGO Dashboard")
with st.container():
    st.subheader("About NGO")

    st.write("""Our NGO helps:
                -Volunteers
                -Animals
                -Environment
            """)

name=st.text_input("Enter your name")

if st.button("Submit"):
    st.success(f"Welcome, {name}")

menu=st.sidebar.selectbox(
    "Menu",["Home","Volunteers","Events"]
)

if menu == "Home":
    st.header("Home Page")

if menu == "Volunteers":
    st.header("Volunteers Details")

if menu == "Events":
    st.header("Event Management")

col1,col2,col3 = st.columns(3)

col1.metric("Volunteers",120)
col2.metric("Events",15)
col3.metric("Attendance","89%")