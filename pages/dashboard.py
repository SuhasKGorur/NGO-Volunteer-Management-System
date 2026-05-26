import streamlit as st
import mysql.connector
import pandas as pd
from database import *

def show_Dashboard():
    st.write("Welcome to our NGO Dashboard")
    with st.container():
            st.subheader("About NGO")

            st.write("""Our NGO helps:
                            -Volunteers
                            -Animals
                            -Environment
                    """)

            #Dashboard Page
            st.header("Dashboard")

            cursor.execute("select count(*)from volunteers")

            total_volunteers=cursor.fetchone()[0]

            cursor.execute("""

            select departments.department_name,
            count(*)
            from volunteers
            join departments
                           
            on volunteers.department_id =
            departments.department_id
                           
            group by departments.department_name

            """)
            
            department_data = cursor.fetchall()

            df=pd.DataFrame(department_data,
                            columns=["Department","Volunteer Count"])
            
            st.bar_chart(df.set_index("Department"))

            #col1,col2,col3,col4 = st.columns(4)
            col1,col2,col3,col4 = st.columns([1,1,1,1]) #ratios of col width

            with col1:
                col1.metric("Total Volunteers",total_volunteers)
            with col2:
                col2.metric("Events",15)
            with col3:
                col3.metric("Attendance","89%")
            with col4:
                col4.metric("Departments",len(department_data))
            
            
            with st.expander("View Department Details"):
                st.dataframe(department_data)


            #Attendance Section
            st.header("Attendance Management")

            cursor.execute(
                "select id, name from volunteers")
            
            volunteers=cursor.fetchall()
            st.dataframe(volunteers)

            #Events Management
            st.header("Events Management")
            cursor.execute(
                "select event_id, event_name from events")
            events=cursor.fetchall()
            st.dataframe(events)

            volunteer_options = {
                name: vid
                for vid, name in volunteers
            }

            event_options = {
                name: eid
                for eid, name in events
            }

            selected_volunteer = st.selectbox(
                "Select Volunteer",
                volunteer_options.keys(),
                key="attendance_volunteer"
            )

            selected_event = st.selectbox(
                "Select Event",
                event_options.keys(),
                key="attendance_event"
            )

            status = st.radio(
                "Attendance Status",
                ["Present", "Absent"]
            )

            if st.button("Mark attendance"):
                volunteer_id = volunteer_options[selected_volunteer]
                event_id = event_options[selected_event]

                query = """
                insert into attendance
                (volunteer_id, event_id, status)
                values (%s, %s, %s)"""

                values=(volunteer_id,event_id,status)

                cursor.execute(query,values)
                conn.commit()
                st.success("Attendance Marked")