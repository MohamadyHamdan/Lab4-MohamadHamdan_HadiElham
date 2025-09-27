"""
Database module providing SQLite database operations for the School Management System.

This module handles all database interactions including table creation,
CRUD operations for students, instructors, courses, and registrations,
as well as database backup functionality.
"""

import sqlite3
import shutil

# Database file name
DB_NAME = 'school.db'

def get_connection() -> sqlite3.Connection:
    """
    Get a database connection to the school database.
    
    :return: SQLite database connection object.
    :rtype: sqlite3.Connection
    """
    return sqlite3.connect(DB_NAME)

def create_tables() -> None:
    """
    Create all necessary database tables if they don't exist.
    
    Creates four tables: students, instructors, courses, and registrations.
    Sets up proper foreign key relationships between tables.
    """
    with get_connection() as conn:
        c = conn.cursor()
        
        # Students table
        c.execute('''CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL
        )''')
        
        # Instructors table
        c.execute('''CREATE TABLE IF NOT EXISTS instructors (
            instructor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL
        )''')
        
        # Courses table with optional instructor assignment
        c.execute('''CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            instructor_id TEXT,
            FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
        )''')
        
        # Student course registrations (many-to-many relationship)
        c.execute('''CREATE TABLE IF NOT EXISTS registrations (
            student_id TEXT,
            course_id TEXT,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        )''')
        
        conn.commit()

def backup_database(backup_path: str) -> None:
    """
    Create a backup of the database.
    
    :param backup_path: Path where the backup file should be saved.
    :type backup_path: str
    :raises IOError: If backup file cannot be created.
    """
    shutil.copyfile(DB_NAME, backup_path)

# --- CRUD Operations ---
# Students
def add_student(student_id: str, name: str, age: int, email: str) -> None:
    """
    Add a new student to the database.
    
    :param student_id: Unique identifier for the student.
    :type student_id: str
    :param name: Student's full name.
    :type name: str
    :param age: Student's age in years.
    :type age: int
    :param email: Student's email address.
    :type email: str
    :raises sqlite3.IntegrityError: If student_id already exists.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO students (student_id, name, age, email) VALUES (?, ?, ?, ?)',
                  (student_id, name, age, email))
        conn.commit()

def get_students() -> list[tuple]:
    """
    Retrieve all students from the database.
    
    :return: List of tuples containing (student_id, name, age, email).
    :rtype: list[tuple]
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT student_id, name, age, email FROM students')
        return c.fetchall()

def update_student(student_id: str, name: str, age: int, email: str) -> None:
    """
    Update an existing student's information.
    
    :param student_id: Student ID to update.
    :type student_id: str
    :param name: Updated student name.
    :type name: str
    :param age: Updated student age.
    :type age: int
    :param email: Updated student email.
    :type email: str
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('UPDATE students SET name=?, age=?, email=? WHERE student_id=?',
                  (name, age, email, student_id))
        conn.commit()

def delete_student(student_id: str) -> None:
    """
    Delete a student and all their course registrations.
    
    :param student_id: Student ID to delete.
    :type student_id: str
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM students WHERE student_id=?', (student_id,))
        c.execute('DELETE FROM registrations WHERE student_id=?', (student_id,))
        conn.commit()

# Instructors
def add_instructor(instructor_id: str, name: str, age: int, email: str) -> None:
    """
    Add a new instructor to the database.
    
    :param instructor_id: Unique identifier for the instructor.
    :type instructor_id: str
    :param name: Instructor's full name.
    :type name: str
    :param age: Instructor's age in years.
    :type age: int
    :param email: Instructor's email address.
    :type email: str
    :raises sqlite3.IntegrityError: If instructor_id already exists.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO instructors (instructor_id, name, age, email) VALUES (?, ?, ?, ?)',
                  (instructor_id, name, age, email))
        conn.commit()

def get_instructors() -> list[tuple]:
    """
    Retrieve all instructors from the database.
    
    :return: List of tuples containing (instructor_id, name, age, email).
    :rtype: list[tuple]
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT instructor_id, name, age, email FROM instructors')
        return c.fetchall()

def update_instructor(instructor_id: str, name: str, age: int, email: str) -> None:
    """
    Update an existing instructor's information.
    
    :param instructor_id: Instructor ID to update.
    :type instructor_id: str
    :param name: Updated instructor name.
    :type name: str
    :param age: Updated instructor age.
    :type age: int
    :param email: Updated instructor email.
    :type email: str
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('UPDATE instructors SET name=?, age=?, email=? WHERE instructor_id=?',
                  (name, age, email, instructor_id))
        conn.commit()

def delete_instructor(instructor_id: str) -> None:
    """
    Delete an instructor and unassign them from all courses.
    
    :param instructor_id: Instructor ID to delete.
    :type instructor_id: str
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM instructors WHERE instructor_id=?', (instructor_id,))
        c.execute('UPDATE courses SET instructor_id=NULL WHERE instructor_id=?', (instructor_id,))
        conn.commit()

# Courses
def add_course(course_id: str, course_name: str, instructor_id: str = None) -> None:
    """
    Add a new course to the database.
    
    :param course_id: Unique identifier for the course.
    :type course_id: str
    :param course_name: Name of the course.
    :type course_name: str
    :param instructor_id: ID of instructor assigned to the course, defaults to None.
    :type instructor_id: str, optional
    :raises sqlite3.IntegrityError: If course_id already exists.
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO courses (course_id, course_name, instructor_id) VALUES (?, ?, ?)',
                  (course_id, course_name, instructor_id))
        conn.commit()

def get_courses() -> list[tuple]:
    """
    Retrieve all courses from the database.
    
    :return: List of tuples containing (course_id, course_name, instructor_id).
    :rtype: list[tuple]
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT course_id, course_name, instructor_id FROM courses')
        return c.fetchall()

def update_course(course_id: str, course_name: str, instructor_id: str) -> None:
    """
    Update an existing course's information.
    
    :param course_id: Course ID to update.
    :type course_id: str
    :param course_name: Updated course name.
    :type course_name: str
    :param instructor_id: Updated instructor ID (can be None).
    :type instructor_id: str
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('UPDATE courses SET course_name=?, instructor_id=? WHERE course_id=?',
                  (course_name, instructor_id, course_id))
        conn.commit()

def delete_course(course_id: str) -> None:
    """
    Delete a course and all its student registrations.
    
    :param course_id: Course ID to delete.
    :type course_id: str
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM courses WHERE course_id=?', (course_id,))
        c.execute('DELETE FROM registrations WHERE course_id=?', (course_id,))
        conn.commit()

# Registrations
def register_student(student_id: str, course_id: str) -> None:
    """
    Register a student for a course.
    
    :param student_id: Student ID to register.
    :type student_id: str
    :param course_id: Course ID to register for.
    :type course_id: str
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO registrations (student_id, course_id) VALUES (?, ?)',
                  (student_id, course_id))
        conn.commit()

def get_registrations() -> list[tuple]:
    """
    Retrieve all student course registrations.
    
    :return: List of tuples containing (student_id, course_id).
    :rtype: list[tuple]
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT student_id, course_id FROM registrations')
        return c.fetchall()

def unregister_student(student_id: str, course_id: str) -> None:
    """
    Unregister a student from a course.
    
    :param student_id: Student ID to unregister.
    :type student_id: str
    :param course_id: Course ID to unregister from.
    :type course_id: str
    """
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM registrations WHERE student_id=? AND course_id=?', (student_id, course_id))
        conn.commit()
