import streamlit as st
import mysql.connector
import pandas as pd
from database import *

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

    st.markdown("---")

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
    
    #usage of tabs
    tab1,tab2=st.tabs(["Analytics","Volunteers"])

    with tab1:
        st.write("Analytics")
    with tab2:
        st.write("Volunteers data")

    