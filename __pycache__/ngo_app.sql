CREATE TABLE admins
(
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

INSERT INTO admins(admin_name,email,password)
VALUES
('Administrator','admin@ngo.com','admin123');

CREATE TABLE ngos
(
    ngo_id INT AUTO_INCREMENT PRIMARY KEY,

    ngo_name VARCHAR(150) NOT NULL,

    registration_no VARCHAR(50) UNIQUE,

    email VARCHAR(100) UNIQUE,

    phone VARCHAR(15),

    address TEXT,

    password VARCHAR(100) NOT NULL,

    status ENUM('Pending','Approved','Rejected')
    DEFAULT 'Pending'
);

CREATE TABLE departments
(
    department_id INT AUTO_INCREMENT PRIMARY KEY,

    department_name VARCHAR(100) UNIQUE NOT NULL,

    description TEXT
);

INSERT INTO departments(department_name,description)
VALUES

('Animal Welfare','Animal rescue and adoption'),

('Environment','Plantation and awareness'),

('Food Donation','Food distribution'),

('Education','Teaching underprivileged'),

('Healthcare','Medical camps');


CREATE TABLE volunteers
(
    volunteer_id INT AUTO_INCREMENT PRIMARY KEY,

    ngo_id INT NOT NULL,

    department_id INT NOT NULL,

    volunteer_name VARCHAR(100) NOT NULL,

    gender ENUM('Male','Female','Other'),

    age INT,

    phone VARCHAR(15),

    email VARCHAR(100) UNIQUE,

    password VARCHAR(100),

    joining_date DATE,

    FOREIGN KEY(ngo_id)
    REFERENCES ngos(ngo_id)
    ON DELETE CASCADE,

    FOREIGN KEY(department_id)
    REFERENCES departments(department_id)
);

CREATE TABLE events
(
    event_id INT AUTO_INCREMENT PRIMARY KEY,

    ngo_id INT,

    event_name VARCHAR(150),

    event_date DATE,

    location VARCHAR(150),

    description TEXT,

    FOREIGN KEY(ngo_id)
    REFERENCES ngos(ngo_id)
    ON DELETE CASCADE
);

CREATE TABLE attendance
(
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,

    volunteer_id INT,

    event_id INT,

    attendance_status ENUM('Present','Absent'),

    FOREIGN KEY(volunteer_id)
    REFERENCES volunteers(volunteer_id)
    ON DELETE CASCADE,

    FOREIGN KEY(event_id)
    REFERENCES events(event_id)
    ON DELETE CASCADE
);

CREATE TABLE event_registrations
(
    registration_id INT AUTO_INCREMENT PRIMARY KEY,

    volunteer_id INT,

    event_id INT,

    registration_date DATE,

    FOREIGN KEY(volunteer_id)
    REFERENCES volunteers(volunteer_id)
    ON DELETE CASCADE,

    FOREIGN KEY(event_id)
    REFERENCES events(event_id)
    ON DELETE CASCADE
);


--------------------------------------------
#LATER CHANGEs DONE
--------------------------------------------

ALTER TABLE ngos
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN approved_by INT NULL,
ADD CONSTRAINT fk_admin
FOREIGN KEY (approved_by)
REFERENCES admins(admin_id);

ALTER TABLE volunteers
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE events
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE attendance
ADD COLUMN marked_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
