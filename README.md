# NGO Volunteer Management System

This is a mini project developed using Python and Streamlit for managing NGO volunteer activities efficiently.

The project helps in:
- Managing volunteer details
- Organizing events
- Tracking attendance
- Viewing dashboard statistics

## Technologies Used

- Python
- Streamlit
- MySQL
- Pandas

## Features

- Volunteer Registration
- Login System
- Dashboard
- Event Management
- Attendance Tracking
- Search Volunteers
- Simple Analytics

## Project Structure

```bash
NGO_Volunteer_System/
│
├── app.py
├── database.py
├── auth.py
├── requirements.txt
├── README.md
│
├── pages/
│   ├── dashboard.py
│   ├── volunteers.py
│   ├── events.py
│   ├── attendance.py
│   ├── admin.py
│
├── assets/
│   ├── style.css
│   ├── images/
│
└── utils/
    ├── helpers.py
```

## How to Run the Project

1. Install required packages

```bash
pip install streamlit mysql-connector-python pandas
```

2. Run the application

```bash
streamlit run app.py
```

## Purpose of the Project

The purpose of this project is to simplify volunteer management activities in NGOs using a simple and user-friendly interface.

This project was developed as part of a Python mini project.

## Future Improvements

- Email Notifications
- Report Generation
- Cloud Database Integration
- Mobile Responsive UI
- Role-based Authentication

## Author

Developed by Suhas K Gorur