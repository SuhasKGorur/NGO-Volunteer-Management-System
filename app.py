import streamlit as st
import mysql.connector
import pandas as pd
from database import *
from pages.dashboard import *
from pages.volunteers import *

st.set_page_config(
    page_title="NGO Volunteer System",
    layout="wide"
)
              

def show_events():

    st.header("Event Management")

    event_name = st.text_input("Event Name")

    event_date = st.date_input("Event Date")

    if st.button("Create Event"):

        st.success("Event Created")

st.sidebar.title("NGO System")
menu=st.sidebar.selectbox(
                    "Navigation",["Dashboard","Volunteers","Events"]
                )

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.title("NGO Volunteer System")

if not st.session_state.logged_in:

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if username == "admin" and password == "1234":

            st.session_state.logged_in = True

            st.success("Login Successful")
            show_Dashboard()
              
        else:
            st.error("Invalid Credentials")

else:

    st.header("Welcome Admin")

    st.write("Dashboard Loaded")

if st.session_state.logged_in:
    if st.button("Logout"):
        st.session_state.logged_in = False


if st.session_state.logged_in:

    if menu == "Volunteers":
        show_Volunteers()     

    # EVENTS PAGE
    elif menu == "Events":
        show_events()

    elif menu == "Dashboard":
        show_Dashboard()

