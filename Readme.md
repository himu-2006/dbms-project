# ExamSeater: Seating & Invigilation Planner

ExamSeater is a web-based application designed to manage university examination scheduling, student seating arrangements, and invigilator assignments. It provides a clean, modern interface for administrators to manage exams, rooms, students, and invigilators, and features an automated, server-side greedy algorithm for assigning seats.

This project is built as a complete Database Management System (DBMS) application, integrating a Python Flask backend with a MySQL database and a dynamic vanilla JavaScript frontend.

## Core Features

The application is divided into several key modules, all accessible from the main navigation sidebar:

* **Dashboard**: Provides a quick overview with statistics for the total number of exams, students, and rooms.
* **Exams Management**: Allows for the creation and viewing of exam slots, including course code, date, and start/end times.
* **Rooms Management**: Define examination halls and rooms with details like room code, capacity, building, and floor number.
* **Students Management**: Add, view, and delete student records, including their roll number, name, and department.
* **Invigilators Management**: Maintain a list of invigilators with their name, employee number, and department.
* **Seat Assignment**: A dedicated page to:
    * Select an exam from a dropdown menu.
    * Run a server-side greedy algorithm to assign all registered students to seats in the available rooms (sorted by capacity).
    * View the resulting assignments, broken down by room.
    * Clear all existing seat assignments.
* **Data Export**: An API endpoint allows for exporting key database tables (courses, exams, rooms, students) into a JSON file.

## Tech Stack

* **Backend**: Flask (Python).
* **Database**: MySQL.
* **ORM**: SQLAlchemy with Flask-Migrate.
* **Frontend**: HTML, CSS, and vanilla JavaScript (ES6+ with `async/await` and `fetch`).
* **Templating**: Jinja2.

## Setup and Installation

1.  **Prerequisites**:
    * Python 3.x and `pip`.
    * A running MySQL server.

2.  **Database Configuration**:
    * Log in to your MySQL server.
    * Create the database. The default name in the application is `dbms`.
        ```sql
        CREATE DATABASE dbms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        ```
    * Use the newly created database:
        ```sql
        USE dbms;
        ```
    * Execute the entire `sql.sql` file against your `dbms` database. This will create all the required tables and populate them with sample data.

3.  **Application Configuration**:
    * Open `app.py`.
    * Update the database connection variables at the top of the file to match your MySQL setup:
        ```python
        DB_USER = "root"
        DB_PASS = ""            # <-- Set your MySQL password here
        DB_HOST = "127.0.0.1"
        DB_PORT = 3306
        DB_NAME = "dbms"
        ```

4.  **Install Dependencies**:
    * Install the required Python packages using pip.
        ```bash
        pip install flask flask-sqlalchemy flask-migrate pymysql
        ```
        *(Note: `pymysql` is used as the MySQL driver)*

5.  **Run the Application**:
    * Execute the `app.py` file to start the Flask development server.
        ```bash
        python app.py
        ```
    * The application will be running at `http://127.0.0.1:5000/`.

## Database Schema

The database structure is defined using SQLAlchemy models in `app.py` and created in `sql.sql`. The key tables include:

* **Core Entities**:
    * `course`: Stores course information (e.g., `CS101`, `Introduction to Programming`).
    * `exams`: Contains scheduled exams, linked to a `course_code`.
    * `rooms`: Stores room details, including `room_code` and `capacity`.
    * `students`: Holds student data, with a unique `roll_no`.
    * `invigilators`: Stores invigilator details with a unique `employee_no`.

* **Junction & Assignment Tables**:
    * `student_exam`: A junction table mapping `student_id` to `exam_id` to signify registration.
    * `seat_assignment`: The main assignment table that maps a `student_id` to a `room_id` and `seat_number` for a specific `exam_id`.
    * `invigilator_availability`: Tracks available dates and times for invigilators.
    * `invigilation_assignment`: Assigns an `invigilator_id` to a `room_id` for a specific `exam_id`.

## API Endpoints

The application serves HTML pages and also provides a RESTful API for frontend data handling:

* `GET /api/state`: Fetches the entire application state (all exams, rooms, students, etc.) for populating the UI.
* `POST /api/rooms`: Adds a new room.
* `POST /api/exams`: Adds a new exam.
* `POST /api/students`: Adds a new student.
* `DELETE /api/students/<int:sid>`: Deletes a student.
* `POST /api/invigilators`: Adds a new invigilator.
* `DELETE /api/invigilators/<int:iid>`: Deletes an invigilator.
* `POST /api/register_all`: Registers all students for a given `exam_id` (demo convenience function).
* `POST /api/assign/<int:exam_id>`: Runs the server-side seat assignment algorithm for the given exam.
* `POST /api/clear_assign`: Deletes all records from the `seat_assignment` table.
* `GET /api/export`: Downloads a JSON file of the core database tables.
