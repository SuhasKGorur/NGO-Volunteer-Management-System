# database.py
# Handles all database connections and query execution

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",   # Change to your MySQL password
    "database": "ngo_app"
}


def get_connection():
    """Create and return a MySQL database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Connection error: {e}")
        return None


def execute_query(query, params=None):
    """Execute INSERT, UPDATE, DELETE. Returns True on success."""
    conn = get_connection()

    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return True

    except Error as e:
        print(f"Execute error: {e}")
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()


def fetch_one(query, params=None):
    """Execute SELECT and return one row as dictionary."""
    conn = get_connection()

    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchone()

    except Error as e:
        print(f"Fetch one error: {e}")
        return None

    finally:
        cursor.close()
        conn.close()


def fetch_all(query, params=None):
    """Execute SELECT and return all rows as list of dictionaries."""
    conn = get_connection()

    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchall()

    except Error as e:
        print(f"Fetch all error: {e}")
        return []

    finally:
        cursor.close()
        conn.close()


def setup_database():
    """Create database and all tables on first run."""

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )

        cursor = conn.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS ngo_app")
        cursor.execute("USE ngo_app")

        # -------------------- Admins --------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                admin_id INT AUTO_INCREMENT PRIMARY KEY,
                admin_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            )
        """)

        # -------------------- NGOs --------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ngos (
                ngo_id INT AUTO_INCREMENT PRIMARY KEY,
                ngo_name VARCHAR(150) NOT NULL,
                registration_no VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(15),
                address TEXT,
                password VARCHAR(100) NOT NULL,
                status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_by INT,
                FOREIGN KEY (approved_by)
                    REFERENCES admins(admin_id)
                    ON DELETE SET NULL
            )
        """)

        # -------------------- Departments --------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INT AUTO_INCREMENT PRIMARY KEY,
                department_name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT
            )
        """)

        # -------------------- Volunteers --------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS volunteers (
                volunteer_id INT AUTO_INCREMENT PRIMARY KEY,
                ngo_id INT NOT NULL,
                department_id INT,
                volunteer_name VARCHAR(100) NOT NULL,
                gender ENUM('Male','Female','Other') NOT NULL,
                age INT,
                phone VARCHAR(15),
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                joining_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ngo_id)
                    REFERENCES ngos(ngo_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
                    ON DELETE SET NULL
            )
        """)

        # -------------------- Events --------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id INT AUTO_INCREMENT PRIMARY KEY,
                ngo_id INT NOT NULL,
                event_name VARCHAR(150) NOT NULL,
                event_date DATE NOT NULL,
                location VARCHAR(200),
                description TEXT,
                event_status ENUM('Upcoming','Completed','Cancelled')
                    DEFAULT 'Upcoming',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ngo_id)
                    REFERENCES ngos(ngo_id)
                    ON DELETE CASCADE
            )
        """)

        # -------------------- Attendance --------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                volunteer_id INT NOT NULL,
                event_id INT NOT NULL,
                attendance_status ENUM('Present','Absent') NOT NULL,
                marked_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (volunteer_id)
                    REFERENCES volunteers(volunteer_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (event_id)
                    REFERENCES events(event_id)
                    ON DELETE CASCADE
            )
        """)

        # -------------------- Event Registrations --------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_registrations (
                registration_id INT AUTO_INCREMENT PRIMARY KEY,
                volunteer_id INT NOT NULL,
                event_id INT NOT NULL,
                registration_date DATE,
                FOREIGN KEY (volunteer_id)
                    REFERENCES volunteers(volunteer_id)
                    ON DELETE CASCADE,
                FOREIGN KEY (event_id)
                    REFERENCES events(event_id)
                    ON DELETE CASCADE
            )
        """)

        # -------------------- Default Admin --------------------
        cursor.execute("SELECT COUNT(*) AS cnt FROM admins")
        row = cursor.fetchone()

        if row[0] == 0:
            cursor.execute("""
                INSERT INTO admins (admin_name, email, password)
                VALUES (
                    'Super Admin',
                    'admin@ngo.com',
                    'admin123'
                )
            """)

        conn.commit()
        print("Setup complete.")
        print("Admin Login:")
        print("Email: admin@ngo.com")
        print("Password: admin123")

    except Error as e:
        print(f"Setup error: {e}")

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    setup_database()