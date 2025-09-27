"""
Main GUI module for the School Management System using PyQt5.

This module provides the complete graphical user interface for managing
students, instructors, courses, and registrations. It includes tabbed
interface, data validation, database operations, and import/export functionality.

The application features:
- Student management with course registration
- Instructor management with course assignment
- Course management with instructor assignment
- Registration management for student-course relationships
- Data validation with user-friendly error messages
- Database backup and restore functionality
- JSON import/export capabilities
- Search functionality across all entities
- Modern PyQt5 interface with professional styling

Example:
    To run the application:
    
    .. code-block:: python
    
        if __name__ == '__main__':
            app = QApplication(sys.argv)
            window = SchoolManagementSystem()
            window.show()
            sys.exit(app.exec_())

Dependencies:
    PyQt5: Modern Qt-based GUI toolkit
    db: Database operations module
    validation: Data validation framework

Author:
    Hadi Elham

Version:
    1.0.0
"""

import sys
import csv
import json
import re
import os
from datetime import datetime

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

# Database and validation imports
from db import (
    create_tables, backup_database,
    add_student, get_students, update_student, delete_student,
    add_instructor, get_instructors, update_instructor, delete_instructor,
    add_course, get_courses, update_course, delete_course,
    register_student, get_registrations, unregister_student, get_connection
)
from validation import DataValidator, ValidationError

class SchoolManagementSystem(QMainWindow):
    """
    Main application window for the School Management System.
    
    Provides a tabbed interface for managing students, instructors, courses,
    and registrations. Includes database operations and data import/export.
    
    :ivar tabs: Tab widget containing all management tabs.
    :vartype tabs: QTabWidget
    :ivar student_tab: Student management tab.
    :vartype student_tab: StudentTab
    :ivar instructor_tab: Instructor management tab.
    :vartype instructor_tab: InstructorTab
    :ivar course_tab: Course management tab.
    :vartype course_tab: CourseTab
    :ivar registration_tab: Registration management tab.
    :vartype registration_tab: RegistrationTab
    """
    
    def __init__(self) -> None:
        """
        Initialize the main application window.
        
        Sets up the database, creates the UI layout, and initializes all tabs.
        """
        super().__init__()
        
        # Initialize database
        create_tables()
        
        # Set up the main window
        self.setWindowTitle('School Management System')
        self.setGeometry(100, 100, 1100, 700)
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Top button bar for database operations
        btn_layout = QHBoxLayout()
        backup_btn = QPushButton('Backup Database')
        backup_btn.clicked.connect(self.backup_db)
        save_json_btn = QPushButton('Save JSON')
        save_json_btn.clicked.connect(self.save_json)
        load_json_btn = QPushButton('Load JSON')
        load_json_btn.clicked.connect(self.load_json)
        
        btn_layout.addWidget(backup_btn)
        btn_layout.addWidget(save_json_btn)
        btn_layout.addWidget(load_json_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        # Create tab widget for different sections
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        self.setCentralWidget(main_widget)
        
        # Initialize all tabs
        self.student_tab = StudentTab(self)
        self.instructor_tab = InstructorTab(self)
        self.course_tab = CourseTab(self)
        self.registration_tab = RegistrationTab(self)
        
        # Add tabs to the widget
        self.tabs.addTab(self.student_tab, 'Students')
        self.tabs.addTab(self.instructor_tab, 'Instructors')
        self.tabs.addTab(self.course_tab, 'Courses')
        self.tabs.addTab(self.registration_tab, 'Registrations')
    def backup_db(self) -> None:
        """
        Create a backup of the database.
        
        Opens a file dialog for the user to choose where to save the backup
        and creates a copy of the current database file. Shows success or
        error messages to inform the user of the operation result.
        
        :raises Exception: If backup operation fails due to file system issues.
        """
        # Let user choose where to save the backup
        path, _ = QFileDialog.getSaveFileName(self, 'Backup Database', '', 'SQLite DB (*.db)')
        if not path:
            return  # User cancelled
        
        try:
            backup_database(path)
            QMessageBox.information(self, 'Backup', 'Database backup successful!')
        except Exception as e:
            QMessageBox.warning(self, 'Backup', f'Error: {e}')
    def save_json(self) -> None:
        """
        Export all school data to a JSON file.
        
        Creates a comprehensive JSON export containing all students, instructors,
        courses, and registrations. The export includes metadata about the export
        date and version, and maintains relationships between entities.
        
        The JSON structure includes:
        - metadata: Export information and version
        - students: Student data with registered courses
        - instructors: Instructor data with assigned courses
        - courses: Course data with enrolled students
        - registrations: Raw registration relationships
        
        :raises Exception: If file operations fail or data processing errors occur.
        """
        try:
            # Let user choose save file
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save School Data', 'school_data.json', 'JSON Files (*.json)')
            if not file_path:
                return
            
            students = get_students()
            instructors = get_instructors()
            courses = get_courses()
            registrations = get_registrations()
            
            # Create unified data structure
            unified_data = {
                'metadata': {
                    'export_date': str(datetime.now()),
                    'version': '1.0',
                    'description': 'School Management System Data Export'
                },
                'students': [],
                'instructors': [],
                'courses': [],
                'registrations': []
            }
            
            # Process students
            for sid, name, age, email in students:
                regs = [r[1] for r in registrations if r[0] == sid]
                unified_data['students'].append({
                    'student_id': sid, 
                    'name': name, 
                    'age': age, 
                    'email': email, 
                    'registered_courses': regs
                })
            
            # Process instructors
            for iid, name, age, email in instructors:
                assigned = [c[0] for c in courses if c[2] == iid]
                unified_data['instructors'].append({
                    'instructor_id': iid, 
                    'name': name, 
                    'age': age, 
                    'email': email, 
                    'assigned_courses': assigned
                })
            
            # Process courses
            for cid, cname, iid in courses:
                enrolled = [r[0] for r in registrations if r[1] == cid]
                unified_data['courses'].append({
                    'course_id': cid, 
                    'course_name': cname, 
                    'instructor_id': iid, 
                    'enrolled_students': enrolled
                })
            
            # Process registrations (raw data for reference)
            for student_id, course_id in registrations:
                unified_data['registrations'].append({
                    'student_id': student_id,
                    'course_id': course_id
                })
            
            # Save unified data to single file
            with open(file_path, 'w') as f:
                json.dump(unified_data, f, indent=2)
            
            QMessageBox.information(self, 'Save JSON', f'Successfully saved all data to:\n{file_path}')
        except Exception as e:
            QMessageBox.warning(self, 'Save JSON', f'Error: {e}')
    def load_json(self) -> None:
        """
        Import school data from a JSON file.
        
        Loads a previously exported JSON file containing students, instructors,
        courses, and registrations. Clears existing data and replaces it with
        the imported data, maintaining all relationships between entities.
        
        The import process:
        1. Validates file format and required sections
        2. Clears existing database tables
        3. Loads instructors first (required for course assignments)
        4. Loads courses with instructor assignments
        5. Loads students and their course registrations
        6. Refreshes all UI components
        
        :raises Exception: If file operations fail, JSON parsing errors, or data validation errors occur.
        """
        try:
            # Let user choose JSON file to load
            file_path, _ = QFileDialog.getOpenFileName(self, 'Load School Data', '', 'JSON Files (*.json)')
            if not file_path:
                return
            
            # Check if file exists
            if not os.path.exists(file_path):
                QMessageBox.warning(self, 'Load JSON', f'File not found: {file_path}')
                return
            
            # Load unified JSON file
            with open(file_path, 'r') as f:
                unified_data = json.load(f)
            
            # Validate data structure
            required_sections = ['students', 'instructors', 'courses', 'registrations']
            missing_sections = [section for section in required_sections if section not in unified_data]
            
            if missing_sections:
                QMessageBox.warning(self, 'Load JSON', f'Invalid file format. Missing sections: {", ".join(missing_sections)}')
                return
            
            # Clear tables
            with get_connection() as conn:
                c = conn.cursor()
                c.execute('DELETE FROM registrations')
                c.execute('DELETE FROM courses')
                c.execute('DELETE FROM students')
                c.execute('DELETE FROM instructors')
                conn.commit()
            
            # Load instructors first
            for inst in unified_data['instructors']:
                add_instructor(inst['instructor_id'], inst['name'], int(inst['age']), inst['email'])
            
            # Load courses with instructor assignment
            for crs in unified_data['courses']:
                add_course(crs['course_id'], crs['course_name'], crs.get('instructor_id'))
            
            # Load students and registrations
            for stu in unified_data['students']:
                add_student(stu['student_id'], stu['name'], int(stu['age']), stu['email'])
                for cid in stu.get('registered_courses', []):
                    register_student(stu['student_id'], cid)
            
            # Refresh UI
            self.student_tab.refresh()
            self.instructor_tab.refresh()
            self.course_tab.refresh()
            
            # Show metadata if available
            metadata_info = ""
            if 'metadata' in unified_data:
                metadata = unified_data['metadata']
                metadata_info = f"\n\nExport Date: {metadata.get('export_date', 'Unknown')}\nVersion: {metadata.get('version', 'Unknown')}"
            
            QMessageBox.information(self, 'Load JSON', f'Successfully loaded all data from:\n{file_path}{metadata_info}')
        except Exception as e:
            QMessageBox.warning(self, 'Load JSON', f'Error: {e}')

class StudentTab(QWidget):
    """
    Student management tab widget.
    
    Provides interface for adding, editing, deleting, and searching students.
    Includes form validation and course registration functionality.
    
    :ivar main: Reference to main application window.
    :vartype main: SchoolManagementSystem
    :ivar table: Table widget displaying student data.
    :vartype table: QTableWidget
    :ivar name_edit: Text input for student name.
    :vartype name_edit: QLineEdit
    :ivar age_edit: Text input for student age.
    :vartype age_edit: QLineEdit
    :ivar email_edit: Text input for student email.
    :vartype email_edit: QLineEdit
    :ivar id_edit: Text input for student ID.
    :vartype id_edit: QLineEdit
    :ivar course_combo: Dropdown for course selection.
    :vartype course_combo: QComboBox
    :ivar add_btn: Button for adding/updating students.
    :vartype add_btn: QPushButton
    """
    
    def __init__(self, main: 'SchoolManagementSystem') -> None:
        """
        Initialize the student management tab.
        
        :param main: Reference to main application window.
        :type main: SchoolManagementSystem
        """
        super().__init__()
        self.main = main
        layout = QHBoxLayout(self)
        # Left: Table and search
        left = QVBoxLayout()
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Search by name, ID, or email...')
        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self.search)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        left.addLayout(search_layout)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email', 'Courses'])
        self.table.setSelectionBehavior(self.table.SelectRows)
        left.addWidget(self.table)
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton('Edit')
        edit_btn.clicked.connect(self.edit)
        delete_btn = QPushButton('Delete')
        delete_btn.clicked.connect(self.delete)
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(refresh_btn)
        left.addLayout(btn_layout)
        layout.addLayout(left, 2)
        # Right: Form
        form = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.age_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.id_edit = QLineEdit()
        self.course_combo = QComboBox()
        self.course_combo.addItem('Select Course')
        self.add_btn = QPushButton('Add Student')
        self.add_btn.clicked.connect(self.add)
        form.addWidget(QLabel('Name:'))
        form.addWidget(self.name_edit)
        form.addWidget(QLabel('Age:'))
        form.addWidget(self.age_edit)
        form.addWidget(QLabel('Email:'))
        form.addWidget(self.email_edit)
        form.addWidget(QLabel('Student ID:'))
        form.addWidget(self.id_edit)
        form.addWidget(QLabel('Register for Course:'))
        form.addWidget(self.course_combo)
        form.addWidget(self.add_btn)
        layout.addLayout(form, 1)
        self.refresh()
    def refresh(self):
        self.table.setRowCount(0)
        self.course_combo.clear()
        self.course_combo.addItem('Select Course')
        courses = get_courses()
        for c in courses:
            self.course_combo.addItem(f'{c[0]} - {c[1]}')
        students = get_students()
        registrations = get_registrations()
        for s in students:
            student_id, name, age, email = s
            registered_courses = [r[1] for r in registrations if r[0] == student_id]
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(student_id))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(str(age)))
            self.table.setItem(row, 3, QTableWidgetItem(email))
            self.table.setItem(row, 4, QTableWidgetItem(', '.join(registered_courses)))
    def add(self) -> None:
        """
        Add a new student to the system.
        
        Validates the provided student data and adds it to the database.
        Includes comprehensive validation for name, age, email, and student ID.
        Optionally registers the student for a selected course.
        Refreshes the UI and clears the form upon successful addition.
        
        :raises ValidationError: If any validation fails (name, age, email, or ID format).
        :raises Exception: If database operations fail.
        """
        name = self.name_edit.text().strip()
        age = self.age_edit.text().strip()
        email = self.email_edit.text().strip()
        student_id = self.id_edit.text().strip()
        course = self.course_combo.currentText().split(' - ')[0] if self.course_combo.currentIndex() > 0 else None
        
        try:
            # Validate all student data
            validated_name, validated_age, validated_email, validated_id = DataValidator.validate_student_data(
                name, age, email, student_id
            )
            
            # Add student to database
            add_student(validated_id, validated_name, validated_age, validated_email)
            
            # Register for course if selected
            if course and course != 'Select Course':
                register_student(validated_id, course)
            
            # Refresh UI
            self.refresh()
            self.main.course_tab.refresh()
            
            # Clear form
            self.name_edit.clear()
            self.age_edit.clear()
            self.email_edit.clear()
            self.id_edit.clear()
            self.course_combo.setCurrentIndex(0)
            
            QMessageBox.information(self, 'Success', 'Student added successfully!')
            
        except ValidationError as e:
            QMessageBox.warning(self, 'Validation Error', f'Please fix the following errors:\n\n{e.message}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An unexpected error occurred:\n{str(e)}')
    def edit(self) -> None:
        """
        Enter edit mode for the selected student.
        
        Retrieves the selected student from the table and populates
        the form with the student's current data. Changes the form to
        update mode and adds a cancel button for reverting changes.
        
        :raises Exception: If student selection is invalid or student not found.
        """
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Edit', 'Select a student to edit.')
            return
        
        # Store original data for potential cancellation
        self.original_student_id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        age = self.table.item(row, 2).text()
        email = self.table.item(row, 3).text()
        
        # Populate form with existing data
        self.name_edit.setText(name)
        self.age_edit.setText(age)
        self.email_edit.setText(email)
        self.id_edit.setText(self.original_student_id)
        
        # Change button to "Update" mode
        self.add_btn.setText('Update Student')
        self.add_btn.clicked.disconnect()
        self.add_btn.clicked.connect(self.update_student)
        
        # Add cancel button
        if not hasattr(self, 'cancel_btn'):
            self.cancel_btn = QPushButton('Cancel Edit')
            self.cancel_btn.clicked.connect(self.cancel_edit)
            self.add_btn.parent().layout().addWidget(self.cancel_btn)
        self.cancel_btn.show()
        
        self.refresh()
    
    def update_student(self) -> None:
        """
        Update an existing student with validated data.
        
        Validates the form data and updates the student in the database.
        Handles ID changes by updating related registrations and maintaining
        data integrity. Refreshes the UI and resets the form after successful update.
        
        :raises ValidationError: If any validation fails during the update process.
        :raises Exception: If database operations fail.
        """
        name = self.name_edit.text().strip()
        age = self.age_edit.text().strip()
        email = self.email_edit.text().strip()
        student_id = self.id_edit.text().strip()
        
        try:
            # Validate all student data (allow same ID for update)
            validated_name, validated_age, validated_email, validated_id = DataValidator.validate_student_data(
                name, age, email, student_id, is_edit=True, exclude_id=self.original_student_id
            )
            
            # Update student in database
            update_student(self.original_student_id, validated_name, validated_age, validated_email)
            
            # If ID changed, update registrations
            if validated_id != self.original_student_id:
                # Get existing registrations
                registrations = get_registrations()
                student_registrations = [r[1] for r in registrations if r[0] == self.original_student_id]
                
                # Delete old registrations
                for course_id in student_registrations:
                    unregister_student(self.original_student_id, course_id)
                
                # Add new registrations
                for course_id in student_registrations:
                    register_student(validated_id, course_id)
                
                # Delete old student record
                delete_student(self.original_student_id)
            
            # Refresh UI
            self.refresh()
            self.main.course_tab.refresh()
            
            # Reset form and button
            self.cancel_edit()
            
            QMessageBox.information(self, 'Success', 'Student updated successfully!')
            
        except ValidationError as e:
            QMessageBox.warning(self, 'Validation Error', f'Please fix the following errors:\n\n{e.message}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An unexpected error occurred:\n{str(e)}')
    
    def cancel_edit(self):
        """Cancel edit mode and reset form"""
        # Clear form
        self.name_edit.clear()
        self.age_edit.clear()
        self.email_edit.clear()
        self.id_edit.clear()
        self.course_combo.setCurrentIndex(0)
        
        # Reset button
        self.add_btn.setText('Add Student')
        self.add_btn.clicked.disconnect()
        self.add_btn.clicked.connect(self.add)
        
        # Hide cancel button
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.hide()
        
        # Clear original data
        if hasattr(self, 'original_student_id'):
            delattr(self, 'original_student_id')
    
    def delete(self) -> None:
        """
        Delete the selected student from the system.
        
        Removes the selected student from the database along with all
        their course registrations. Refreshes the UI to reflect the changes.
        
        :raises Exception: If student selection is invalid or deletion fails.
        """
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Delete', 'Select a student to delete.')
            return
        student_id = self.table.item(row, 0).text()
        delete_student(student_id)
        self.refresh()
        self.main.course_tab.refresh()
    def search(self) -> None:
        """
        Search and filter students based on the provided query.
        
        Searches through student names, IDs, and email addresses for matches
        with the query string. Case-insensitive search that updates the
        table to show only matching students.
        """
        query = self.search_edit.text().strip().lower()
        self.table.setRowCount(0)
        students = get_students()
        registrations = get_registrations()
        for s in students:
            student_id, name, age, email = s
            if (query in name.lower() or query in student_id.lower() or query in email.lower()):
                registered_courses = [r[1] for r in registrations if r[0] == student_id]
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(student_id))
                self.table.setItem(row, 1, QTableWidgetItem(name))
                self.table.setItem(row, 2, QTableWidgetItem(str(age)))
                self.table.setItem(row, 3, QTableWidgetItem(email))
                self.table.setItem(row, 4, QTableWidgetItem(', '.join(registered_courses)))

class InstructorTab(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        layout = QHBoxLayout(self)
        # Left: Table and search
        left = QVBoxLayout()
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Search by name, ID, or email...')
        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self.search)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        left.addLayout(search_layout)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email', 'Courses'])
        self.table.setSelectionBehavior(self.table.SelectRows)
        left.addWidget(self.table)
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton('Edit')
        edit_btn.clicked.connect(self.edit)
        delete_btn = QPushButton('Delete')
        delete_btn.clicked.connect(self.delete)
        self.assign_course_btn = QPushButton('Assign Course')
        self.assign_course_btn.clicked.connect(self.assign_course)
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(self.assign_course_btn)
        btn_layout.addWidget(refresh_btn)
        left.addLayout(btn_layout)
        layout.addLayout(left, 2)
        # Right: Form
        form = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.age_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.id_edit = QLineEdit()
        self.course_combo = QComboBox()
        self.course_combo.addItem('Select Course')
        self.add_btn = QPushButton('Add Instructor')
        self.add_btn.clicked.connect(self.add)
        form.addWidget(QLabel('Name:'))
        form.addWidget(self.name_edit)
        form.addWidget(QLabel('Age:'))
        form.addWidget(self.age_edit)
        form.addWidget(QLabel('Email:'))
        form.addWidget(self.email_edit)
        form.addWidget(QLabel('Instructor ID:'))
        form.addWidget(self.id_edit)
        form.addWidget(QLabel('Assign to Course:'))
        form.addWidget(self.course_combo)
        form.addWidget(self.add_btn)
        layout.addLayout(form, 1)
        self.refresh()
    def refresh(self):
        self.table.setRowCount(0)
        self.course_combo.clear()
        self.course_combo.addItem('Select Course')
        courses = get_courses()
        for c in courses:
            self.course_combo.addItem(f'{c[0]} - {c[1]}')
        instructors = get_instructors()
        for i in instructors:
            instructor_id, name, age, email = i
            assigned_courses = [c[0] for c in courses if c[2] == instructor_id]
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(instructor_id))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(str(age)))
            self.table.setItem(row, 3, QTableWidgetItem(email))
            self.table.setItem(row, 4, QTableWidgetItem(', '.join(assigned_courses)))
    def add(self) -> None:
        """
        Add a new instructor to the system.
        
        Validates the provided instructor data and adds it to the database.
        Includes comprehensive validation for name, age, email, and instructor ID.
        Optionally assigns the instructor to a selected course.
        Refreshes the UI and clears the form upon successful addition.
        
        :raises ValidationError: If any validation fails (name, age, email, or ID format).
        :raises Exception: If database operations fail.
        """
        name = self.name_edit.text().strip()
        age = self.age_edit.text().strip()
        email = self.email_edit.text().strip()
        instructor_id = self.id_edit.text().strip()
        course = self.course_combo.currentText().split(' - ')[0] if self.course_combo.currentIndex() > 0 else None
        
        try:
            # Validate all instructor data
            validated_name, validated_age, validated_email, validated_id = DataValidator.validate_instructor_data(
                name, age, email, instructor_id
            )
            
            # Add instructor to database
            add_instructor(validated_id, validated_name, validated_age, validated_email)
            
            # Assign to course if selected
            if course and course != 'Select Course':
                update_course(course, None, validated_id)
            
            # Refresh UI
            self.refresh()
            self.main.course_tab.refresh()
            
            # Clear form
            self.name_edit.clear()
            self.age_edit.clear()
            self.email_edit.clear()
            self.id_edit.clear()
            self.course_combo.setCurrentIndex(0)
            
            QMessageBox.information(self, 'Success', 'Instructor added successfully!')
            
        except ValidationError as e:
            QMessageBox.warning(self, 'Validation Error', f'Please fix the following errors:\n\n{e.message}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An unexpected error occurred:\n{str(e)}')
    def edit(self) -> None:
        """
        Enter edit mode for the selected instructor.
        
        Retrieves the selected instructor from the table and populates
        the form with the instructor's current data. Changes the form to
        update mode and adds a cancel button for reverting changes.
        
        :raises Exception: If instructor selection is invalid or instructor not found.
        """
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Edit', 'Select an instructor to edit.')
            return
        
        # Store original data for potential cancellation
        self.original_instructor_id = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        age = self.table.item(row, 2).text()
        email = self.table.item(row, 3).text()
        
        # Populate form with existing data
        self.name_edit.setText(name)
        self.age_edit.setText(age)
        self.email_edit.setText(email)
        self.id_edit.setText(self.original_instructor_id)
        
        # Change button to "Update" mode
        self.add_btn.setText('Update Instructor')
        self.add_btn.clicked.disconnect()
        self.add_btn.clicked.connect(self.update_instructor)
        
        # Add cancel button
        if not hasattr(self, 'cancel_btn'):
            self.cancel_btn = QPushButton('Cancel Edit')
            self.cancel_btn.clicked.connect(self.cancel_edit)
            self.add_btn.parent().layout().addWidget(self.cancel_btn)
        self.cancel_btn.show()
        
        self.refresh()
    
    def update_instructor(self) -> None:
        """
        Update an existing instructor with validated data.
        
        Validates the form data and updates the instructor in the database.
        Handles ID changes by updating related course assignments and maintaining
        data integrity. Refreshes the UI and resets the form after successful update.
        
        :raises ValidationError: If any validation fails during the update process.
        :raises Exception: If database operations fail.
        """
        name = self.name_edit.text().strip()
        age = self.age_edit.text().strip()
        email = self.email_edit.text().strip()
        instructor_id = self.id_edit.text().strip()
        
        try:
            # Validate all instructor data (allow same ID for update)
            validated_name, validated_age, validated_email, validated_id = DataValidator.validate_instructor_data(
                name, age, email, instructor_id, is_edit=True, exclude_id=self.original_instructor_id
            )
            
            # Update instructor in database
            update_instructor(self.original_instructor_id, validated_name, validated_age, validated_email)
            
            # If ID changed, update course assignments
            if validated_id != self.original_instructor_id:
                # Get courses assigned to this instructor
                courses = get_courses()
                assigned_courses = [c[0] for c in courses if c[2] == self.original_instructor_id]
                
                # Update course assignments
                for course_id in assigned_courses:
                    update_course(course_id, None, validated_id)
                
                # Delete old instructor record
                delete_instructor(self.original_instructor_id)
            
            # Refresh UI
            self.refresh()
            self.main.course_tab.refresh()
            
            # Reset form and button
            self.cancel_edit()
            
            QMessageBox.information(self, 'Success', 'Instructor updated successfully!')
            
        except ValidationError as e:
            QMessageBox.warning(self, 'Validation Error', f'Please fix the following errors:\n\n{e.message}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An unexpected error occurred:\n{str(e)}')
    
    def cancel_edit(self):
        """Cancel edit mode and reset form"""
        # Clear form
        self.name_edit.clear()
        self.age_edit.clear()
        self.email_edit.clear()
        self.id_edit.clear()
        self.course_combo.setCurrentIndex(0)
        
        # Reset button
        self.add_btn.setText('Add Instructor')
        self.add_btn.clicked.disconnect()
        self.add_btn.clicked.connect(self.add)
        
        # Hide cancel button
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.hide()
        
        # Clear original data
        if hasattr(self, 'original_instructor_id'):
            delattr(self, 'original_instructor_id')
    
    def delete(self) -> None:
        """
        Delete the selected instructor from the system.
        
        Removes the selected instructor from the database and unassigns them
        from all courses. Refreshes the UI to reflect the changes.
        
        :raises Exception: If instructor selection is invalid or deletion fails.
        """
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Delete', 'Select an instructor to delete.')
            return
        instructor_id = self.table.item(row, 0).text()
        delete_instructor(instructor_id)
        self.refresh()
        self.main.course_tab.refresh()
    
    def assign_course(self):
        """Assign a course to a selected instructor"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Assign Course', 'Please select an instructor to assign a course to.')
            return
        
        instructor_id = self.table.item(row, 0).text()
        instructor_name = self.table.item(row, 1).text()
        
        # Show dialog to select course
        from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Assign Course')
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f'Assign course to instructor: {instructor_name} ({instructor_id})'))
        
        course_combo = QComboBox()
        course_combo.addItem('No Course')
        courses = get_courses()
        for course_id, course_name, course_instructor_id in courses:
            # Only show courses that don't already have an instructor
            if not course_instructor_id:
                course_combo.addItem(f'{course_id} - {course_name}')
        
        layout.addWidget(QLabel('Select Course:'))
        layout.addWidget(course_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_course = course_combo.currentText()
            if selected_course == 'No Course':
                QMessageBox.information(self, 'Info', 'No course selected.')
                return
            
            course_id = selected_course.split(' - ')[0]
            course_name = selected_course.split(' - ', 1)[1]
            
            try:
                # Update course with new instructor
                update_course(course_id, course_name, instructor_id)
                
                # Refresh UI
                self.refresh()
                self.main.course_tab.refresh()
                
                QMessageBox.information(self, 'Success', 'Course assigned successfully!')
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to assign course:\n{str(e)}')
    
    def search(self) -> None:
        """
        Search and filter instructors based on the provided query.
        
        Searches through instructor names, IDs, and email addresses for matches
        with the query string. Case-insensitive search that updates the
        table to show only matching instructors.
        """
        query = self.search_edit.text().strip().lower()
        self.table.setRowCount(0)
        instructors = get_instructors()
        courses = get_courses()
        for i in instructors:
            instructor_id, name, age, email = i
            if (query in name.lower() or query in instructor_id.lower() or query in email.lower()):
                assigned_courses = [c[0] for c in courses if c[2] == instructor_id]
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(instructor_id))
                self.table.setItem(row, 1, QTableWidgetItem(name))
                self.table.setItem(row, 2, QTableWidgetItem(str(age)))
                self.table.setItem(row, 3, QTableWidgetItem(email))
                self.table.setItem(row, 4, QTableWidgetItem(', '.join(assigned_courses)))

class CourseTab(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        layout = QHBoxLayout(self)
        # Left: Table and search
        left = QVBoxLayout()
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText('Search by ID, name, or instructor...')
        search_btn = QPushButton('Search')
        search_btn.clicked.connect(self.search)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        left.addLayout(search_layout)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'Instructor', 'Students'])
        self.table.setSelectionBehavior(self.table.SelectRows)
        left.addWidget(self.table)
        btn_layout = QHBoxLayout()
        edit_btn = QPushButton('Edit')
        edit_btn.clicked.connect(self.edit)
        delete_btn = QPushButton('Delete')
        delete_btn.clicked.connect(self.delete)
        self.assign_instructor_btn = QPushButton('Assign Instructor')
        self.assign_instructor_btn.clicked.connect(self.assign_instructor)
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(self.assign_instructor_btn)
        btn_layout.addWidget(refresh_btn)
        left.addLayout(btn_layout)
        layout.addLayout(left, 2)
        # Right: Form
        form = QVBoxLayout()
        self.id_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.instructor_combo = QComboBox()
        self.instructor_combo.addItem('Select Instructor')
        self.add_btn = QPushButton('Add Course')
        self.add_btn.clicked.connect(self.add)
        form.addWidget(QLabel('Course ID:'))
        form.addWidget(self.id_edit)
        form.addWidget(QLabel('Course Name:'))
        form.addWidget(self.name_edit)
        form.addWidget(QLabel('Assign Instructor:'))
        form.addWidget(self.instructor_combo)
        form.addWidget(self.add_btn)
        layout.addLayout(form, 1)
        self.refresh()
    def refresh(self):
        self.table.setRowCount(0)
        self.instructor_combo.clear()
        self.instructor_combo.addItem('Select Instructor')
        instructors = get_instructors()
        for i in instructors:
            self.instructor_combo.addItem(f'{i[0]} - {i[1]}')
        courses = get_courses()
        registrations = get_registrations()
        for c in courses:
            course_id, course_name, instructor_id = c
            instructor = next((i[1] for i in instructors if i[0] == instructor_id), '')
            enrolled_students = [r[0] for r in registrations if r[1] == course_id]
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(course_id))
            self.table.setItem(row, 1, QTableWidgetItem(course_name))
            self.table.setItem(row, 2, QTableWidgetItem(instructor))
            self.table.setItem(row, 3, QTableWidgetItem(', '.join(enrolled_students)))
    def add(self) -> None:
        """
        Add a new course to the system.
        
        Validates the provided course data and adds it to the database.
        Includes comprehensive validation for course ID, name, and instructor ID.
        Refreshes the UI and clears the form upon successful addition.
        
        :raises ValidationError: If any validation fails (ID format, name, or instructor existence).
        :raises Exception: If database operations fail.
        """
        course_id = self.id_edit.text().strip()
        course_name = self.name_edit.text().strip()
        instructor_id = self.instructor_combo.currentText().split(' - ')[0] if self.instructor_combo.currentIndex() > 0 else None
        
        try:
            # Validate course data (instructor is required)
            validated_id, validated_name, validated_instructor_id = DataValidator.validate_course_data(
                course_id, course_name, instructor_id
            )
            
            # Add course to database
            add_course(validated_id, validated_name, validated_instructor_id)
            
            # Refresh UI
            self.refresh()
            self.main.student_tab.refresh()
            self.main.instructor_tab.refresh()
            
            # Clear form
            self.id_edit.clear()
            self.name_edit.clear()
            self.instructor_combo.setCurrentIndex(0)
            
            QMessageBox.information(self, 'Success', 'Course added successfully!')
            
        except ValidationError as e:
            QMessageBox.warning(self, 'Validation Error', f'Please fix the following errors:\n\n{e.message}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An unexpected error occurred:\n{str(e)}')
    def edit(self) -> None:
        """
        Enter edit mode for the selected course.
        
        Retrieves the selected course from the table and populates
        the form with the course's current data. Changes the form to
        update mode and adds a cancel button for reverting changes.
        
        :raises Exception: If course selection is invalid or course not found.
        """
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Edit', 'Select a course to edit.')
            return
        
        # Store original data for potential cancellation
        self.original_course_id = self.table.item(row, 0).text()
        course_name = self.table.item(row, 1).text()
        instructor = self.table.item(row, 2).text()
        
        # Populate form with existing data
        self.id_edit.setText(self.original_course_id)
        self.name_edit.setText(course_name)
        
        # Set instructor combo (find by instructor name)
        if instructor:
            for i in range(self.instructor_combo.count()):
                if instructor in self.instructor_combo.itemText(i):
                    self.instructor_combo.setCurrentIndex(i)
                    break
        
        # Change button to "Update" mode
        self.add_btn.setText('Update Course')
        self.add_btn.clicked.disconnect()
        self.add_btn.clicked.connect(self.update_course)
        
        # Add cancel button
        if not hasattr(self, 'cancel_btn'):
            self.cancel_btn = QPushButton('Cancel Edit')
            self.cancel_btn.clicked.connect(self.cancel_edit)
            self.add_btn.parent().layout().addWidget(self.cancel_btn)
        self.cancel_btn.show()
        
        self.refresh()
    
    def update_course(self) -> None:
        """
        Update an existing course with validated data.
        
        Validates the form data and updates the course in the database.
        Handles ID changes by updating related registrations and maintaining
        data integrity. Refreshes the UI and resets the form after successful update.
        
        :raises ValidationError: If any validation fails during the update process.
        :raises Exception: If database operations fail.
        """
        course_id = self.id_edit.text().strip()
        course_name = self.name_edit.text().strip()
        instructor_id = self.instructor_combo.currentText().split(' - ')[0] if self.instructor_combo.currentIndex() > 0 else None
        
        try:
            # Validate course data (instructor is required, allow same ID for update)
            validated_id, validated_name, validated_instructor_id = DataValidator.validate_course_data(
                course_id, course_name, instructor_id, exclude_id=self.original_course_id
            )
            
            # Update course in database
            update_course(self.original_course_id, validated_name, validated_instructor_id)
            
            # If ID changed, update registrations
            if validated_id != self.original_course_id:
                # Get existing registrations
                registrations = get_registrations()
                course_registrations = [r[0] for r in registrations if r[1] == self.original_course_id]
                
                # Delete old registrations
                for student_id in course_registrations:
                    unregister_student(student_id, self.original_course_id)
                
                # Add new registrations
                for student_id in course_registrations:
                    register_student(student_id, validated_id)
                
                # Delete old course record
                delete_course(self.original_course_id)
            
            # Refresh UI
            self.refresh()
            self.main.student_tab.refresh()
            self.main.instructor_tab.refresh()
            
            # Reset form and button
            self.cancel_edit()
            
            QMessageBox.information(self, 'Success', 'Course updated successfully!')
            
        except ValidationError as e:
            QMessageBox.warning(self, 'Validation Error', f'Please fix the following errors:\n\n{e.message}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An unexpected error occurred:\n{str(e)}')
    
    def cancel_edit(self):
        """Cancel edit mode and reset form"""
        # Clear form
        self.id_edit.clear()
        self.name_edit.clear()
        self.instructor_combo.setCurrentIndex(0)
        
        # Reset button
        self.add_btn.setText('Add Course')
        self.add_btn.clicked.disconnect()
        self.add_btn.clicked.connect(self.add)
        
        # Hide cancel button
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.hide()
        
        # Clear original data
        if hasattr(self, 'original_course_id'):
            delattr(self, 'original_course_id')
    
    def delete(self) -> None:
        """
        Delete the selected course from the system.
        
        Removes the selected course from the database along with all
        student registrations. Refreshes the UI to reflect the changes.
        
        :raises Exception: If course selection is invalid or deletion fails.
        """
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Delete', 'Select a course to delete.')
            return
        course_id = self.table.item(row, 0).text()
        delete_course(course_id)
        self.refresh()
        self.main.student_tab.refresh()
        self.main.instructor_tab.refresh()
    
    def assign_instructor(self):
        """Assign an instructor to a selected course"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Assign Instructor', 'Please select a course to assign an instructor to.')
            return
        
        course_id = self.table.item(row, 0).text()
        course_name = self.table.item(row, 1).text()
        
        # Get current instructor
        current_instructor = self.table.item(row, 2).text()
        
        # Show dialog to select instructor
        from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QComboBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle('Assign Instructor')
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f'Assign instructor to course: {course_name} ({course_id})'))
        
        instructor_combo = QComboBox()
        instructor_combo.addItem('No Instructor')
        instructors = get_instructors()
        for instructor_id, name, age, email in instructors:
            instructor_combo.addItem(f'{instructor_id} - {name}')
        
        # Set current instructor if any
        if current_instructor:
            for i in range(instructor_combo.count()):
                if current_instructor in instructor_combo.itemText(i):
                    instructor_combo.setCurrentIndex(i)
                    break
        
        layout.addWidget(QLabel('Select Instructor:'))
        layout.addWidget(instructor_combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_instructor = instructor_combo.currentText()
            if selected_instructor == 'No Instructor':
                instructor_id = None
            else:
                instructor_id = selected_instructor.split(' - ')[0]
            
            try:
                # Update course with new instructor
                update_course(course_id, course_name, instructor_id)
                
                # Refresh UI
                self.refresh()
                self.main.instructor_tab.refresh()
                
                QMessageBox.information(self, 'Success', 'Instructor assigned successfully!')
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to assign instructor:\n{str(e)}')
    
    def search(self) -> None:
        """
        Search and filter courses based on the provided query.
        
        Searches through course IDs, names, and instructor names for matches
        with the query string. Case-insensitive search that updates the
        table to show only matching courses.
        """
        query = self.search_edit.text().strip().lower()
        self.table.setRowCount(0)
        courses = get_courses()
        instructors = get_instructors()
        registrations = get_registrations()
        for c in courses:
            course_id, course_name, instructor_id = c
            instructor = next((i[1] for i in instructors if i[0] == instructor_id), '')
            if (query in course_id.lower() or query in course_name.lower() or query in instructor.lower()):
                enrolled_students = [r[0] for r in registrations if r[1] == course_id]
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(course_id))
                self.table.setItem(row, 1, QTableWidgetItem(course_name))
                self.table.setItem(row, 2, QTableWidgetItem(instructor))
                self.table.setItem(row, 3, QTableWidgetItem(', '.join(enrolled_students)))

class RegistrationTab(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Registration form
        form_layout = QFormLayout()
        
        # Student selection
        self.student_combo = QComboBox()
        self.student_combo.addItem('Select Student')
        form_layout.addRow('Student:', self.student_combo)
        
        # Course selection
        self.course_combo = QComboBox()
        self.course_combo.addItem('Select Course')
        form_layout.addRow('Course:', self.course_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.register_btn = QPushButton('Register Student')
        self.unregister_btn = QPushButton('Unregister Student')
        self.refresh_btn = QPushButton('Refresh')
        
        self.register_btn.clicked.connect(self.register_student)
        self.unregister_btn.clicked.connect(self.unregister_student)
        self.refresh_btn.clicked.connect(self.refresh)
        
        button_layout.addWidget(self.register_btn)
        button_layout.addWidget(self.unregister_btn)
        button_layout.addWidget(self.refresh_btn)
        
        # Registration table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Student ID', 'Student Name', 'Course ID', 'Course Name'])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('Search:'))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.search)
        search_layout.addWidget(self.search_edit)
        search_layout.addStretch()
        
        # Add to main layout
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel('Current Registrations:'))
        layout.addWidget(self.table)
        layout.addLayout(search_layout)
        
        self.setLayout(layout)
        self.refresh()
    
    def refresh(self):
        """Refresh all data"""
        self.refresh_student_combo()
        self.refresh_course_combo()
        self.refresh_table()
    
    def refresh_student_combo(self):
        """Refresh student dropdown"""
        self.student_combo.clear()
        self.student_combo.addItem('Select Student')
        students = get_students()
        for student_id, name, age, email in students:
            self.student_combo.addItem(f'{student_id} - {name}')
    
    def refresh_course_combo(self):
        """Refresh course dropdown"""
        self.course_combo.clear()
        self.course_combo.addItem('Select Course')
        courses = get_courses()
        for course_id, course_name, instructor_id in courses:
            self.course_combo.addItem(f'{course_id} - {course_name}')
    
    def refresh_table(self):
        """Refresh registration table"""
        self.table.setRowCount(0)
        registrations = get_registrations()
        students = {s[0]: s[1] for s in get_students()}  # student_id: name
        courses = {c[0]: c[1] for c in get_courses()}  # course_id: name
        
        for student_id, course_id in registrations:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(student_id))
            self.table.setItem(row, 1, QTableWidgetItem(students.get(student_id, 'Unknown')))
            self.table.setItem(row, 2, QTableWidgetItem(course_id))
            self.table.setItem(row, 3, QTableWidgetItem(courses.get(course_id, 'Unknown')))
    
    def register_student(self) -> None:
        """
        Register the selected student for the selected course.
        
        Validates that both a student and course are selected, checks for
        existing registrations to prevent duplicates, and creates the
        registration relationship in the database.
        
        :raises Exception: If registration fails or validation errors occur.
        """
        student_text = self.student_combo.currentText()
        course_text = self.course_combo.currentText()
        
        if student_text == 'Select Student' or course_text == 'Select Course':
            QMessageBox.warning(self, 'Registration', 'Please select both a student and a course.')
            return
        
        student_id = student_text.split(' - ')[0]
        course_id = course_text.split(' - ')[0]
        
        try:
            # Check if already registered
            registrations = get_registrations()
            if (student_id, course_id) in registrations:
                QMessageBox.warning(self, 'Registration', 'Student is already registered for this course.')
                return
            
            # Register student
            register_student(student_id, course_id)
            
            # Refresh UI
            self.refresh_table()
            self.main.student_tab.refresh()
            self.main.course_tab.refresh()
            
            QMessageBox.information(self, 'Success', 'Student registered successfully!')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Registration failed:\n{str(e)}')
    
    def unregister_student(self) -> None:
        """
        Unregister the selected student from the selected course.
        
        Validates that both a student and course are selected, checks for
        existing registrations, and removes the registration relationship
        from the database.
        
        :raises Exception: If unregistration fails or validation errors occur.
        """
        student_text = self.student_combo.currentText()
        course_text = self.course_combo.currentText()
        
        if student_text == 'Select Student' or course_text == 'Select Course':
            QMessageBox.warning(self, 'Unregistration', 'Please select both a student and a course.')
            return
        
        student_id = student_text.split(' - ')[0]
        course_id = course_text.split(' - ')[0]
        
        try:
            # Check if registered
            registrations = get_registrations()
            if (student_id, course_id) not in registrations:
                QMessageBox.warning(self, 'Unregistration', 'Student is not registered for this course.')
                return
            
            # Unregister student
            unregister_student(student_id, course_id)
            
            # Refresh UI
            self.refresh_table()
            self.main.student_tab.refresh()
            self.main.course_tab.refresh()
            
            QMessageBox.information(self, 'Success', 'Student unregistered successfully!')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Unregistration failed:\n{str(e)}')
    
    def search(self) -> None:
        """
        Search and filter registrations based on the provided query.
        
        Searches through student IDs, student names, course IDs, and course names
        for matches with the query string. Case-insensitive search that updates
        the table to show only matching registrations.
        """
        query = self.search_edit.text().strip().lower()
        self.table.setRowCount(0)
        registrations = get_registrations()
        students = {s[0]: s[1] for s in get_students()}
        courses = {c[0]: c[1] for c in get_courses()}
        
        for student_id, course_id in registrations:
            student_name = students.get(student_id, 'Unknown')
            course_name = courses.get(course_id, 'Unknown')
            
            if (query in student_id.lower() or query in student_name.lower() or 
                query in course_id.lower() or query in course_name.lower()):
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(student_id))
                self.table.setItem(row, 1, QTableWidgetItem(student_name))
                self.table.setItem(row, 2, QTableWidgetItem(course_id))
                self.table.setItem(row, 3, QTableWidgetItem(course_name))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SchoolManagementSystem()
    window.show()
    sys.exit(app.exec_())
