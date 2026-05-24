import streamlit as st
import mysql.connector
import pandas as pd

conn = mysql.connector.connect(

    host="localhost",

    user="root",

    password="root",

    database="ngo_app"
)

cursor = conn.cursor()

st.set_page_config(
    page_title="NGO Volunteer System",
    layout="wide"
)

def show_Volunteers():
    st.subheader("Search Volunteers")
    search_name = st.text_input("Enter name to search")

    query = """ select 
                volunteers.id,
                volunteers.name,
                volunteers.age,
                departments.department_name

                from volunteers
                join departments on

                volunteers.department_id =
                departments.department_id
                where name like %s """
    
    cursor.execute(query,(f"%{search_name}%",))

    data=cursor.fetchall()

    st.dataframe(data)

    #Filter
    department_filter = st.selectbox(

    "Filter by Department",

    [
        "All",
        "Environment",
        "Animal Welfare",
        "Education"
    ]
    )

    department_map={
            "All" :0,
            "Environment" :1,
            "Animal Welfare":2,
            "Education" :3
    }

    new_department_id=department_map[department_filter]

    if department_filter == "All":

        cursor.execute(
            """select 
                volunteers.id,
                volunteers.name,
                volunteers.age,
                departments.department_name

                from volunteers
                join departments on
                
                volunteers.department_id =
                departments.department_id
                """
        )

    else:

        cursor.execute(

            """
            select 
            volunteers.id,
            volunteers.name,
            volunteers.age,
            departments.department_name

            from volunteers
            join departments on

            volunteers.department_id =
            departments.department_id
            WHERE volunteers.department_id = %s
            """, (new_department_id,)
        )

    data = cursor.fetchall()

    st.dataframe(data)

    with st.form("volunteer_form"):

            st.subheader("Volunteer Registration")

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Name")

            with col2:
                age = st.number_input("Age",min_value=18,max_value=100)

            department = st.selectbox(
                "Department",
                ["Environment", "Animal Welfare", "Education"]
            )

            new_department_id=department_map[department]

            gender = st.radio(
                "Gender",
                ["Male", "Female", "Other"]
            )

            available = st.checkbox(
                "Available on Weekends"
            )

            submit = st.form_submit_button("Register")
            

            if submit:

                query="""
                    insert into volunteers (name, age,department_id)
                    values (%s,%s,%s)"""
                
                values=(name,age,new_department_id)

                cursor.execute(query,values)

                conn.commit()

                st.success("Volunteer Registered Successfully")

                cursor.execute("""select
                               volunteers.id,
                               volunteers.name,
                               volunteers.age,
                               departments.department_name

                               from volunteers
                               join departments
                               
                               on volunteers.department_id =
                               departments.department_id""")
                data = cursor.fetchall()
                st.dataframe(data)

                st.write("Gender:", gender)
                st.write("Weekend Availability:", available)

    with st.form("update_form"):

        st.subheader("Update Volunteer")
        update_id = st.number_input(
            "Enter Volunteer ID to Update",
            min_value=1,
            step=1
        )
        new_name = st.text_input("New Name")

        new_age = st.number_input(
            "New Age",
            min_value=18,
            max_value=100,
            step=1
        )

        new_department = st.selectbox(
            "New Department",
            [
                "Environment",
                "Animal Welfare",
                "Education"
            ]
        )

        department_map={
            "Environment" :1,
            "Animal Welfare":2,
            "Education" :3
        }

        new_department_id=department_map[new_department]

        if st.form_submit_button("Update Volunteer"):
            query=""" update volunteers
            set name = %s, age = %s, department_id = %s
            where id = %s
            """
            values = (new_name,new_age,new_department_id,update_id)
            
            cursor.execute(query,values)
            conn.commit()
            st.success("Volunteer Updated Successfully")

    with st.form("delete_form"):

        st.subheader("Delete Volunteer")

        delete_id = st.number_input(
            "Enter Volunteer ID to Delete",
            min_value=1,
            step=1,
            key="delete"
        )
        
        delete_submit = st.form_submit_button("Delete Volunteer")
        
        if delete_submit:
            query=""" delete from volunteers
            where id = %s  """

            values = (delete_id,)
            
            cursor.execute(query,values)
            conn.commit()
            st.success("Volunteer Deleted Successfully")
                

def show_events():

    st.header("Event Management")

    event_name = st.text_input("Event Name")

    event_date = st.date_input("Event Date")

    if st.button("Create Event"):

        st.success("Event Created")

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

            col1,col2,col3,col4 = st.columns(4)

            col1.metric("Total Volunteers",total_volunteers)
            col2.metric("Events",15)
            col3.metric("Attendance","89%")
            col4.metric("Departments",len(department_data))
       
            st.dataframe(department_data)


            #Attendance Section
            st.header("Attendance Management")

            cursor.execute(
                "select id, name from volunteers")
            
            volunteers=cursor.fetchall()
            st.dataframe(volunteers)

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
                volunteer_options.keys()
            )

            selected_event = st.selectbox(
                "Select Event",
                event_options.keys()
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

