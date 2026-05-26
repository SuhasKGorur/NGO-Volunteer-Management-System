import mysql.connector
conn = mysql.connector.connect(

    host="localhost",

    user="root",

    password="root",

    database="ngo_app"
)

cursor = conn.cursor()