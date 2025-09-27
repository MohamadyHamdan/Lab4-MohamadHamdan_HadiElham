"""
Main GUI module for the School Management System using Tkinter.

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

Example:
    To run the application:
    
    .. code-block:: python
    
        if __name__ == "__main__":
            root = tk.Tk()
            app = SchoolManagementApp(root)
            root.mainloop()

Dependencies:
    tkinter: Built-in Python GUI toolkit
    forms: Custom form creation utilities
    db: Database operations module
    validation: Data validation framework

Author:
    Hadi Elham

Version:
    1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
from datetime import datetime

# Import form creation functions
from forms import (
    create_student_form, create_instructor_form, create_course_form,
    create_student_treeview, create_instructor_treeview, create_course_treeview,
    create_search_bar, create_edit_delete_buttons
)

# Database operations
from db import (
    create_tables, backup_database,
    add_student, get_students, update_student, delete_student,
    add_instructor, get_instructors, update_instructor, delete_instructor,
    add_course, get_courses, update_course, delete_course,
    register_student, get_registrations, unregister_student, get_connection
)

# Validation
from validation import DataValidator, ValidationError

class SchoolManagementApp:
    """
    Main application class for the School Management System using Tkinter.
    
    This class provides the complete GUI interface for managing students, instructors,
    courses, and registrations. It includes tabbed navigation, form-based data entry,
    data validation, and comprehensive CRUD operations.
    
    The application is organized into four main tabs:
    - Students: Manage student information and course registrations
    - Instructors: Manage instructor information and course assignments
    - Courses: Manage course information and instructor assignments
    - Registrations: Manage student-course enrollment relationships
    
    Features:
        - Tabbed interface for organized navigation
        - Form-based data entry with validation
        - TreeView widgets for data display
        - Search functionality across all entities
        - Edit/Delete operations with confirmation
        - Database backup and restore
        - JSON import/export capabilities
        - Real-time data refresh and updates
    
    :ivar root: Main Tkinter root window.
    :vartype root: tk.Tk
    :ivar notebook: Tabbed widget containing all management tabs.
    :vartype notebook: ttk.Notebook
    :ivar student_tree: TreeView widget for displaying student data.
    :vartype student_tree: ttk.Treeview
    :ivar instructor_tree: TreeView widget for displaying instructor data.
    :vartype instructor_tree: ttk.Treeview
    :ivar course_tree: TreeView widget for displaying course data.
    :vartype course_tree: ttk.Treeview
    :ivar registration_tree: TreeView widget for displaying registration data.
    :vartype registration_tree: ttk.Treeview
    :ivar student_entries: List of Entry widgets for student form.
    :vartype student_entries: list[tk.Entry]
    :ivar instructor_entries: List of Entry widgets for instructor form.
    :vartype instructor_entries: list[tk.Entry]
    :ivar course_entries: List of Entry widgets for course form.
    :vartype course_entries: list[tk.Entry]
    """
    
    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the School Management Application.
        
        Sets up the main window, initializes the database, creates the tabbed
        interface, and configures all UI components for student, instructor,
        course, and registration management.
        
        :param root: Main Tkinter root window.
        :type root: tk.Tk
        """
        # Initialize database
        create_tables()
        
        # Set up main window
        self.root = root
        self.root.title("School Management System")
        self.root.geometry("1000x650")

        # Create top button bar for database operations
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill='x', pady=5)
        
        backup_btn = tk.Button(btn_frame, text="Backup Database", command=self.backup_db)
        backup_btn.pack(side=tk.LEFT, padx=5)
        save_json_btn = tk.Button(btn_frame, text="Save JSON", command=self.save_json)
        save_json_btn.pack(side=tk.LEFT, padx=5)
        load_json_btn = tk.Button(btn_frame, text="Load JSON", command=self.load_json)
        load_json_btn.pack(side=tk.LEFT, padx=5)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Set up all the tabs
        self.setup_student_tab()
        self.setup_instructor_tab()
        self.setup_course_tab()
        self.setup_registration_tab()

    def backup_db(self) -> None:
        """
        Create a backup of the database.
        
        Opens a file dialog for the user to choose where to save the backup
        and creates a copy of the current database file. Shows success or
        error messages to inform the user of the operation result.
        
        :raises Exception: If backup operation fails due to file system issues.
        """
        # Let user choose where to save the backup
        path = filedialog.asksaveasfilename(defaultextension='.db', filetypes=[('SQLite DB', '*.db')])
        if not path:
            return  # User cancelled
        
        try:
            backup_database(path)
            messagebox.showinfo('Backup', 'Database backup successful!')
        except Exception as e:
            messagebox.showwarning('Backup', f'Error: {e}')

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
            file_path = filedialog.asksaveasfilename(
                title='Save School Data',
                defaultextension='.json',
                filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')]
            )
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
            
            messagebox.showinfo('Save JSON', f'Successfully saved all data to:\n{file_path}')
        except Exception as e:
            messagebox.showwarning('Save JSON', f'Error: {e}')

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
            file_path = filedialog.askopenfilename(
                title='Load School Data',
                filetypes=[('JSON Files', '*.json'), ('All Files', '*.*')]
            )
            if not file_path:
                return
            
            # Check if file exists
            if not os.path.exists(file_path):
                messagebox.showwarning('Load JSON', f'File not found: {file_path}')
                return
            
            # Load unified JSON file
            with open(file_path, 'r') as f:
                unified_data = json.load(f)
            
            # Validate data structure
            required_sections = ['students', 'instructors', 'courses', 'registrations']
            missing_sections = [section for section in required_sections if section not in unified_data]
            
            if missing_sections:
                messagebox.showwarning('Load JSON', f'Invalid file format. Missing sections: {", ".join(missing_sections)}')
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
            self.refresh_student_tree()
            self.refresh_instructor_tree()
            self.refresh_course_tree()
            
            # Show metadata if available
            metadata_info = ""
            if 'metadata' in unified_data:
                metadata = unified_data['metadata']
                metadata_info = f"\n\nExport Date: {metadata.get('export_date', 'Unknown')}\nVersion: {metadata.get('version', 'Unknown')}"
            
            messagebox.showinfo('Load JSON', f'Successfully loaded all data from:\n{file_path}{metadata_info}')
        except Exception as e:
            messagebox.showwarning('Load JSON', f'Error: {e}')

    def setup_student_tab(self) -> None:
        """
        Set up the student management tab.
        
        Creates the student management interface with:
        - Search functionality for filtering students
        - TreeView for displaying student data with course registrations
        - Edit/Delete buttons for student operations
        - Form for adding new students
        - Refresh button for updating the display
        
        The tab is organized with a left panel containing the data display
        and controls, and a right panel containing the input form.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Students')

        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill='both', expand=True)
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill='y')

        search_bar, self.student_search_var = create_search_bar(left_frame, self.search_students)
        search_bar.pack(fill='x', pady=2)
        self.student_tree = create_student_treeview(left_frame)
        self.student_tree.pack(expand=True, fill='both', pady=2)
        btns = create_edit_delete_buttons(left_frame, self.edit_student, self.delete_student)
        btns.pack(pady=2)
        refresh_btn = tk.Button(left_frame, text="Refresh", command=self.refresh_student_tree)
        refresh_btn.pack(pady=2)

        form, self.student_entries = create_student_form(right_frame, self.add_student)
        form.pack(pady=2)
        self.refresh_student_tree()

    def setup_instructor_tab(self) -> None:
        """
        Set up the instructor management tab.
        
        Creates the instructor management interface with:
        - Search functionality for filtering instructors
        - TreeView for displaying instructor data with assigned courses
        - Edit/Delete buttons for instructor operations
        - Assign Course button for course assignment
        - Form for adding new instructors
        - Refresh button for updating the display
        
        The tab is organized with a left panel containing the data display
        and controls, and a right panel containing the input form.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Instructors')

        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill='both', expand=True)
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill='y')

        search_bar, self.instructor_search_var = create_search_bar(left_frame, self.search_instructors)
        search_bar.pack(fill='x', pady=2)
        self.instructor_tree = create_instructor_treeview(left_frame)
        self.instructor_tree.pack(expand=True, fill='both', pady=2)
        btns = create_edit_delete_buttons(left_frame, self.edit_instructor, self.delete_instructor)
        btns.pack(pady=2)
        assign_course_btn = tk.Button(left_frame, text="Assign Course", command=self.assign_course)
        assign_course_btn.pack(pady=2)
        refresh_btn = tk.Button(left_frame, text="Refresh", command=self.refresh_instructor_tree)
        refresh_btn.pack(pady=2)

        form, self.instructor_entries = create_instructor_form(right_frame, self.add_instructor)
        form.pack(pady=2)
        self.refresh_instructor_tree()

    def setup_course_tab(self) -> None:
        """
        Set up the course management tab.
        
        Creates the course management interface with:
        - Search functionality for filtering courses
        - TreeView for displaying course data with instructor and enrolled students
        - Edit/Delete buttons for course operations
        - Assign Instructor button for instructor assignment
        - Form for adding new courses
        - Refresh button for updating the display
        
        The tab is organized with a left panel containing the data display
        and controls, and a right panel containing the input form.
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='Courses')

        left_frame = ttk.Frame(frame)
        left_frame.pack(side=tk.LEFT, fill='both', expand=True)
        right_frame = ttk.Frame(frame)
        right_frame.pack(side=tk.RIGHT, fill='y')

        search_bar, self.course_search_var = create_search_bar(left_frame, self.search_courses)
        search_bar.pack(fill='x', pady=2)
        self.course_tree = create_course_treeview(left_frame)
        self.course_tree.pack(expand=True, fill='both', pady=2)
        btns = create_edit_delete_buttons(left_frame, self.edit_course, self.delete_course)
        btns.pack(pady=2)
        assign_instructor_btn = tk.Button(left_frame, text="Assign Instructor", command=self.assign_instructor)
        assign_instructor_btn.pack(pady=2)
        refresh_btn = tk.Button(left_frame, text="Refresh", command=self.refresh_course_tree)
        refresh_btn.pack(pady=2)

        form, self.course_entries = create_course_form(right_frame, self.add_course)
        form.pack(pady=2)
        self.refresh_course_tree()

    # --- Student Logic ---
    def add_student(self, name: str, age: str, email: str, student_id: str) -> None:
        """
        Add a new student to the system.
        
        Validates the provided student data and adds it to the database.
        Includes comprehensive validation for name, age, email, and student ID.
        Refreshes the UI and clears the form upon successful addition.
        
        :param name: Student's full name.
        :type name: str
        :param age: Student's age as string.
        :type age: str
        :param email: Student's email address.
        :type email: str
        :param student_id: Unique identifier for the student.
        :type student_id: str
        
        :raises ValidationError: If any validation fails (name, age, email, or ID format).
        :raises Exception: If database operations fail.
        """
        try:
            # Validate all student data
            validated_name, validated_age, validated_email, validated_id = DataValidator.validate_student_data(
                name, age, email, student_id
            )
            
            # Add student to database
            add_student(validated_id, validated_name, validated_age, validated_email)
            
            # Refresh UI
            self.refresh_student_tree()
            for entry in self.student_entries:
                entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Student added successfully!")
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", f"Please fix the following errors:\n\n{e.message}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

    def refresh_student_tree(self) -> None:
        """
        Refresh the student TreeView with current data from the database.
        
        Clears the existing tree data and repopulates it with all students
        from the database, including their registered courses. This method
        is called after any data modification to keep the display current.
        """
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)
        students = get_students()
        registrations = get_registrations()
        for s in students:
            student_id, name, age, email = s
            registered_courses = [r[1] for r in registrations if r[0] == student_id]
            self.student_tree.insert('', 'end', values=(student_id, name, age, email, ', '.join(registered_courses)))

    def search_students(self, query: str) -> None:
        """
        Search and filter students based on the provided query.
        
        Searches through student names, IDs, and email addresses for matches
        with the query string. Case-insensitive search that updates the
        TreeView to show only matching students.
        
        :param query: Search term to filter students by.
        :type query: str
        """
        query = query.lower()
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)
        students = get_students()
        registrations = get_registrations()
        for s in students:
            student_id, name, age, email = s
            if (query in name.lower() or query in student_id.lower() or query in email.lower()):
                registered_courses = [r[1] for r in registrations if r[0] == student_id]
                self.student_tree.insert('', 'end', values=(student_id, name, age, email, ', '.join(registered_courses)))

    def edit_student(self) -> None:
        """
        Enter edit mode for the selected student.
        
        Retrieves the selected student from the TreeView and populates
        the form with the student's current data. Changes the form to
        update mode and adds a cancel button for reverting changes.
        
        :raises Exception: If student selection is invalid or student not found.
        """
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Edit Student", "Please select a student to edit.")
            return
        item = self.student_tree.item(selected[0])
        student_id = item['values'][0]
        students = get_students()
        student = next((s for s in students if s[0] == student_id), None)
        if not student:
            messagebox.showerror("Edit Student", "Student not found.")
            return
        
        # Store original data for potential cancellation
        self.original_student_id = student_id
        
        # Populate form with existing data
        for idx, entry in enumerate(self.student_entries):
            entry.delete(0, tk.END)
        self.student_entries[0].insert(0, student[1])  # name
        self.student_entries[1].insert(0, student[2])  # age
        self.student_entries[2].insert(0, student[3])  # email
        self.student_entries[3].insert(0, student[0])  # student_id
        
        # Change button to "Update" mode
        self.add_btn = self.student_entries[0].master.children['!button']
        self.add_btn.config(text='Update Student', command=self.update_student)
        
        # Add cancel button
        if not hasattr(self, 'cancel_btn'):
            self.cancel_btn = tk.Button(self.student_entries[0].master, text='Cancel Edit', command=self.cancel_edit_student)
            self.cancel_btn.pack(pady=2)
        self.cancel_btn.pack(pady=2)
        
        self.refresh_student_tree()
    
    def update_student(self) -> None:
        """
        Update an existing student with validated data.
        
        Validates the form data and updates the student in the database.
        Handles ID changes by updating related registrations and maintaining
        data integrity. Refreshes the UI and resets the form after successful update.
        
        :raises ValidationError: If any validation fails during the update process.
        :raises Exception: If database operations fail.
        """
        name = self.student_entries[0].get()
        age = self.student_entries[1].get()
        email = self.student_entries[2].get()
        student_id = self.student_entries[3].get()
        
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
            self.refresh_student_tree()
            for entry in self.student_entries:
                entry.delete(0, tk.END)
            
            # Reset button
            self.add_btn.config(text='Add Student', command=self.add_student)
            
            # Hide cancel button
            if hasattr(self, 'cancel_btn'):
                self.cancel_btn.pack_forget()
            
            messagebox.showinfo("Success", "Student updated successfully!")
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", f"Please fix the following errors:\n\n{e.message}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")
    
    def cancel_edit_student(self):
        """Cancel edit mode and reset form"""
        # Clear form
        for entry in self.student_entries:
            entry.delete(0, tk.END)
        
        # Reset button
        self.add_btn.config(text='Add Student', command=self.add_student)
        
        # Hide cancel button
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.pack_forget()
        
        # Clear original data
        if hasattr(self, 'original_student_id'):
            delattr(self, 'original_student_id')

    def delete_student(self) -> None:
        """
        Delete the selected student from the system.
        
        Removes the selected student from the database along with all
        their course registrations. Refreshes the UI to reflect the changes.
        
        :raises Exception: If student selection is invalid or deletion fails.
        """
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showwarning("Delete Student", "Please select a student to delete.")
            return
        item = self.student_tree.item(selected[0])
        student_id = item['values'][0]
        delete_student(student_id)
        self.refresh_student_tree()

    # --- Instructor Logic ---
    def add_instructor(self, name: str, age: str, email: str, instructor_id: str) -> None:
        """
        Add a new instructor to the system.
        
        Validates the provided instructor data and adds it to the database.
        Includes comprehensive validation for name, age, email, and instructor ID.
        Refreshes the UI and clears the form upon successful addition.
        
        :param name: Instructor's full name.
        :type name: str
        :param age: Instructor's age as string.
        :type age: str
        :param email: Instructor's email address.
        :type email: str
        :param instructor_id: Unique identifier for the instructor.
        :type instructor_id: str
        
        :raises ValidationError: If any validation fails (name, age, email, or ID format).
        :raises Exception: If database operations fail.
        """
        try:
            # Validate all instructor data
            validated_name, validated_age, validated_email, validated_id = DataValidator.validate_instructor_data(
                name, age, email, instructor_id
            )
            
            # Add instructor to database
            add_instructor(validated_id, validated_name, validated_age, validated_email)
            
            # Refresh UI
            self.refresh_instructor_tree()
            for entry in self.instructor_entries:
                entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Instructor added successfully!")
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", f"Please fix the following errors:\n\n{e.message}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

    def refresh_instructor_tree(self) -> None:
        """
        Refresh the instructor TreeView with current data from the database.
        
        Clears the existing tree data and repopulates it with all instructors
        from the database, including their assigned courses. This method
        is called after any data modification to keep the display current.
        """
        for row in self.instructor_tree.get_children():
            self.instructor_tree.delete(row)
        instructors = get_instructors()
        courses = get_courses()
        for i in instructors:
            instructor_id, name, age, email = i
            assigned_courses = [c[0] for c in courses if c[2] == instructor_id]
            self.instructor_tree.insert('', 'end', values=(instructor_id, name, age, email, ', '.join(assigned_courses)))

    def search_instructors(self, query: str) -> None:
        """
        Search and filter instructors based on the provided query.
        
        Searches through instructor names, IDs, and email addresses for matches
        with the query string. Case-insensitive search that updates the
        TreeView to show only matching instructors.
        
        :param query: Search term to filter instructors by.
        :type query: str
        """
        query = query.lower()
        for row in self.instructor_tree.get_children():
            self.instructor_tree.delete(row)
        instructors = get_instructors()
        courses = get_courses()
        for i in instructors:
            instructor_id, name, age, email = i
            if (query in name.lower() or query in instructor_id.lower() or query in email.lower()):
                assigned_courses = [c[0] for c in courses if c[2] == instructor_id]
                self.instructor_tree.insert('', 'end', values=(instructor_id, name, age, email, ', '.join(assigned_courses)))

    def edit_instructor(self):
        selected = self.instructor_tree.selection()
        if not selected:
            messagebox.showwarning("Edit Instructor", "Please select an instructor to edit.")
            return
        item = self.instructor_tree.item(selected[0])
        instructor_id = item['values'][0]
        instructors = get_instructors()
        instructor = next((i for i in instructors if i[0] == instructor_id), None)
        if not instructor:
            messagebox.showerror("Edit Instructor", "Instructor not found.")
            return
        
        # Store original data for potential cancellation
        self.original_instructor_id = instructor_id
        
        # Populate form with existing data
        for idx, entry in enumerate(self.instructor_entries):
            entry.delete(0, tk.END)
        self.instructor_entries[0].insert(0, instructor[1])  # name
        self.instructor_entries[1].insert(0, instructor[2])  # age
        self.instructor_entries[2].insert(0, instructor[3])  # email
        self.instructor_entries[3].insert(0, instructor[0])  # instructor_id
        
        # Change button to "Update" mode
        self.add_btn = self.instructor_entries[0].master.children['!button']
        self.add_btn.config(text='Update Instructor', command=self.update_instructor)
        
        # Add cancel button
        if not hasattr(self, 'cancel_btn'):
            self.cancel_btn = tk.Button(self.instructor_entries[0].master, text='Cancel Edit', command=self.cancel_edit_instructor)
            self.cancel_btn.pack(pady=2)
        self.cancel_btn.pack(pady=2)
        
        self.refresh_instructor_tree()
    
    def update_instructor(self):
        """Update existing instructor with validation"""
        name = self.instructor_entries[0].get()
        age = self.instructor_entries[1].get()
        email = self.instructor_entries[2].get()
        instructor_id = self.instructor_entries[3].get()
        
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
            self.refresh_instructor_tree()
            for entry in self.instructor_entries:
                entry.delete(0, tk.END)
            
            # Reset button
            self.add_btn.config(text='Add Instructor', command=self.add_instructor)
            
            # Hide cancel button
            if hasattr(self, 'cancel_btn'):
                self.cancel_btn.pack_forget()
            
            messagebox.showinfo("Success", "Instructor updated successfully!")
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", f"Please fix the following errors:\n\n{e.message}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")
    
    def cancel_edit_instructor(self):
        """Cancel edit mode and reset form"""
        # Clear form
        for entry in self.instructor_entries:
            entry.delete(0, tk.END)
        
        # Reset button
        self.add_btn.config(text='Add Instructor', command=self.add_instructor)
        
        # Hide cancel button
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.pack_forget()
        
        # Clear original data
        if hasattr(self, 'original_instructor_id'):
            delattr(self, 'original_instructor_id')

    def delete_instructor(self):
        selected = self.instructor_tree.selection()
        if not selected:
            messagebox.showwarning("Delete Instructor", "Please select an instructor to delete.")
            return
        item = self.instructor_tree.item(selected[0])
        instructor_id = item['values'][0]
        delete_instructor(instructor_id)
        self.refresh_instructor_tree()

    # --- Course Logic ---
    def add_course(self, course_id: str, course_name: str, instructor_id: str) -> None:
        """
        Add a new course to the system.
        
        Validates the provided course data and adds it to the database.
        Includes comprehensive validation for course ID, name, and instructor ID.
        Refreshes the UI and clears the form upon successful addition.
        
        :param course_id: Unique identifier for the course.
        :type course_id: str
        :param course_name: Name of the course.
        :type course_name: str
        :param instructor_id: ID of the instructor assigned to the course.
        :type instructor_id: str
        
        :raises ValidationError: If any validation fails (ID format, name, or instructor existence).
        :raises Exception: If database operations fail.
        """
        try:
            # Validate course data (instructor is required)
            validated_id, validated_name, validated_instructor_id = DataValidator.validate_course_data(
                course_id, course_name, instructor_id
            )
            
            # Add course to database
            add_course(validated_id, validated_name, validated_instructor_id)
            
            # Refresh UI
            self.refresh_course_tree()
            for entry in self.course_entries:
                entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", "Course added successfully!")
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", f"Please fix the following errors:\n\n{e.message}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

    def refresh_course_tree(self) -> None:
        """
        Refresh the course TreeView with current data from the database.
        
        Clears the existing tree data and repopulates it with all courses
        from the database, including their assigned instructors and enrolled students.
        This method is called after any data modification to keep the display current.
        """
        for row in self.course_tree.get_children():
            self.course_tree.delete(row)
        courses = get_courses()
        registrations = get_registrations()
        instructors = get_instructors()
        for c in courses:
            course_id, course_name, instructor_id = c
            instructor_name = next((i[1] for i in instructors if i[0] == instructor_id), '')
            enrolled_students = [r[0] for r in registrations if r[1] == course_id]
            self.course_tree.insert('', 'end', values=(course_id, course_name, instructor_name, ', '.join(enrolled_students)))

    def search_courses(self, query: str) -> None:
        """
        Search and filter courses based on the provided query.
        
        Searches through course IDs, names, and instructor names for matches
        with the query string. Case-insensitive search that updates the
        TreeView to show only matching courses.
        
        :param query: Search term to filter courses by.
        :type query: str
        """
        query = query.lower()
        for row in self.course_tree.get_children():
            self.course_tree.delete(row)
        courses = get_courses()
        instructors = get_instructors()
        registrations = get_registrations()
        for c in courses:
            course_id, course_name, instructor_id = c
            instructor_name = next((i[1] for i in instructors if i[0] == instructor_id), '')
            if (query in course_id.lower() or query in course_name.lower() or query in instructor_name.lower()):
                enrolled_students = [r[0] for r in registrations if r[1] == course_id]
                self.course_tree.insert('', 'end', values=(course_id, course_name, instructor_name, ', '.join(enrolled_students)))

    def edit_course(self):
        selected = self.course_tree.selection()
        if not selected:
            messagebox.showwarning("Edit Course", "Please select a course to edit.")
            return
        item = self.course_tree.item(selected[0])
        course_id = item['values'][0]
        courses = get_courses()
        course = next((c for c in courses if c[0] == course_id), None)
        if not course:
            messagebox.showerror("Edit Course", "Course not found.")
            return
        
        # Store original data for potential cancellation
        self.original_course_id = course_id
        
        # Populate form with existing data
        for idx, entry in enumerate(self.course_entries):
            entry.delete(0, tk.END)
        self.course_entries[0].insert(0, course[0])  # course_id
        self.course_entries[1].insert(0, course[1])  # course_name
        self.course_entries[2].insert(0, course[2] if course[2] else '')  # instructor_id
        
        # Change button to "Update" mode
        self.add_btn = self.course_entries[0].master.children['!button']
        self.add_btn.config(text='Update Course', command=self.update_course)
        
        # Add cancel button
        if not hasattr(self, 'cancel_btn'):
            self.cancel_btn = tk.Button(self.course_entries[0].master, text='Cancel Edit', command=self.cancel_edit_course)
            self.cancel_btn.pack(pady=2)
        self.cancel_btn.pack(pady=2)
        
        self.refresh_course_tree()
    
    def update_course(self):
        """Update existing course with validation"""
        course_id = self.course_entries[0].get()
        course_name = self.course_entries[1].get()
        instructor_id = self.course_entries[2].get()
        
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
            self.refresh_course_tree()
            for entry in self.course_entries:
                entry.delete(0, tk.END)
            
            # Reset button
            self.add_btn.config(text='Add Course', command=self.add_course)
            
            # Hide cancel button
            if hasattr(self, 'cancel_btn'):
                self.cancel_btn.pack_forget()
            
            messagebox.showinfo("Success", "Course updated successfully!")
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", f"Please fix the following errors:\n\n{e.message}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")
    
    def cancel_edit_course(self):
        """Cancel edit mode and reset form"""
        # Clear form
        for entry in self.course_entries:
            entry.delete(0, tk.END)
        
        # Reset button
        self.add_btn.config(text='Add Course', command=self.add_course)
        
        # Hide cancel button
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.pack_forget()
        
        # Clear original data
        if hasattr(self, 'original_course_id'):
            delattr(self, 'original_course_id')

    def delete_course(self):
        selected = self.course_tree.selection()
        if not selected:
            messagebox.showwarning("Delete Course", "Please select a course to delete.")
            return
        item = self.course_tree.item(selected[0])
        course_id = item['values'][0]
        delete_course(course_id)
        self.refresh_course_tree()
    
    def assign_instructor(self):
        """Assign an instructor to a selected course"""
        selected = self.course_tree.selection()
        if not selected:
            messagebox.showwarning("Assign Instructor", "Please select a course to assign an instructor to.")
            return
        
        item = self.course_tree.item(selected[0])
        course_id = item['values'][0]
        course_name = item['values'][1]
        current_instructor = item['values'][2]
        
        # Create assignment dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Instructor")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Dialog content
        ttk.Label(dialog, text=f"Assign instructor to course: {course_name} ({course_id})").pack(pady=10)
        
        ttk.Label(dialog, text="Select Instructor:").pack(pady=5)
        instructor_var = tk.StringVar()
        instructor_combo = ttk.Combobox(dialog, textvariable=instructor_var, state='readonly', width=40)
        instructor_combo.pack(pady=5)
        
        # Populate instructor combo
        instructor_combo['values'] = ['No Instructor'] + [f'{i[0]} - {i[1]}' for i in get_instructors()]
        
        # Set current instructor if any
        if current_instructor:
            for option in instructor_combo['values']:
                if current_instructor in option:
                    instructor_combo.set(option)
                    break
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_assign():
            selected_instructor = instructor_var.get()
            if selected_instructor == 'No Instructor':
                instructor_id = None
            else:
                instructor_id = selected_instructor.split(' - ')[0]
            
            try:
                # Update course with new instructor
                update_course(course_id, course_name, instructor_id)
                
                # Refresh UI
                self.refresh_course_tree()
                self.refresh_instructor_tree()
                
                messagebox.showinfo("Success", "Instructor assigned successfully!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to assign instructor:\n{str(e)}")
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Assign", command=on_assign).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)
    
    def assign_course(self):
        """Assign a course to a selected instructor"""
        selected = self.instructor_tree.selection()
        if not selected:
            messagebox.showwarning("Assign Course", "Please select an instructor to assign a course to.")
            return
        
        item = self.instructor_tree.item(selected[0])
        instructor_id = item['values'][0]
        instructor_name = item['values'][1]
        
        # Create assignment dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Course")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Dialog content
        ttk.Label(dialog, text=f"Assign course to instructor: {instructor_name} ({instructor_id})").pack(pady=10)
        
        ttk.Label(dialog, text="Select Course:").pack(pady=5)
        course_var = tk.StringVar()
        course_combo = ttk.Combobox(dialog, textvariable=course_var, state='readonly', width=40)
        course_combo.pack(pady=5)
        
        # Populate course combo with only unassigned courses
        courses = get_courses()
        unassigned_courses = [f'{c[0]} - {c[1]}' for c in courses if not c[2]]
        course_combo['values'] = ['No Course'] + unassigned_courses
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_assign():
            selected_course = course_var.get()
            if selected_course == 'No Course':
                messagebox.showinfo("Info", "No course selected.")
                dialog.destroy()
                return
            
            course_id = selected_course.split(' - ')[0]
            course_name = selected_course.split(' - ', 1)[1]
            
            try:
                # Update course with new instructor
                update_course(course_id, course_name, instructor_id)
                
                # Refresh UI
                self.refresh_course_tree()
                self.refresh_instructor_tree()
                
                messagebox.showinfo("Success", "Course assigned successfully!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to assign course:\n{str(e)}")
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Assign", command=on_assign).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)

    def setup_registration_tab(self) -> None:
        """
        Set up the registration management tab.
        
        Creates the registration management interface with:
        - Student and course selection dropdowns
        - Register/Unregister buttons for managing enrollments
        - TreeView for displaying current registrations
        - Search functionality for filtering registrations
        - Refresh button for updating the display
        
        The tab provides a centralized interface for managing
        student-course enrollment relationships.
        """
        self.registration_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.registration_frame, text="Registrations")
        
        # Registration form
        form_frame = ttk.LabelFrame(self.registration_frame, text="Register/Unregister Student")
        form_frame.pack(fill='x', padx=10, pady=5)
        
        # Student selection
        ttk.Label(form_frame, text="Student:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.reg_student_var = tk.StringVar()
        self.reg_student_combo = ttk.Combobox(form_frame, textvariable=self.reg_student_var, state='readonly')
        self.reg_student_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Course selection
        ttk.Label(form_frame, text="Course:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.reg_course_var = tk.StringVar()
        self.reg_course_combo = ttk.Combobox(form_frame, textvariable=self.reg_course_var, state='readonly')
        self.reg_course_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Register Student", command=self.register_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Unregister Student", command=self.unregister_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_registration_tab).pack(side=tk.LEFT, padx=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Registration table
        table_frame = ttk.LabelFrame(self.registration_frame, text="Current Registrations")
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Search
        search_frame = ttk.Frame(table_frame)
        search_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.reg_search_var = tk.StringVar()
        self.reg_search_entry = ttk.Entry(search_frame, textvariable=self.reg_search_var)
        self.reg_search_entry.pack(side=tk.LEFT, padx=5, fill='x', expand=True)
        self.reg_search_var.trace('w', self.search_registrations)
        
        # Treeview
        columns = ('Student ID', 'Student Name', 'Course ID', 'Course Name')
        self.registration_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        for col in columns:
            self.registration_tree.heading(col, text=col)
            self.registration_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.registration_tree.yview)
        self.registration_tree.configure(yscrollcommand=scrollbar.set)
        
        self.registration_tree.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        self.refresh_registration_tab()
    
    def refresh_registration_tab(self):
        """Refresh registration tab data"""
        # Refresh student combo
        self.reg_student_combo['values'] = ['Select Student'] + [f'{s[0]} - {s[1]}' for s in get_students()]
        self.reg_student_combo.set('Select Student')
        
        # Refresh course combo
        self.reg_course_combo['values'] = ['Select Course'] + [f'{c[0]} - {c[1]}' for c in get_courses()]
        self.reg_course_combo.set('Select Course')
        
        # Refresh table
        self.refresh_registration_tree()
    
    def refresh_registration_tree(self):
        """Refresh registration tree view"""
        for item in self.registration_tree.get_children():
            self.registration_tree.delete(item)
        
        registrations = get_registrations()
        students = {s[0]: s[1] for s in get_students()}  # student_id: name
        courses = {c[0]: c[1] for c in get_courses()}  # course_id: name
        
        for student_id, course_id in registrations:
            student_name = students.get(student_id, 'Unknown')
            course_name = courses.get(course_id, 'Unknown')
            self.registration_tree.insert('', 'end', values=(student_id, student_name, course_id, course_name))
    
    def register_student(self) -> None:
        """
        Register the selected student for the selected course.
        
        Validates that both a student and course are selected, checks for
        existing registrations to prevent duplicates, and creates the
        registration relationship in the database.
        
        :raises Exception: If registration fails or validation errors occur.
        """
        student_text = self.reg_student_var.get()
        course_text = self.reg_course_var.get()
        
        if student_text == 'Select Student' or course_text == 'Select Course':
            messagebox.showwarning("Registration", "Please select both a student and a course.")
            return
        
        student_id = student_text.split(' - ')[0]
        course_id = course_text.split(' - ')[0]
        
        try:
            # Check if already registered
            registrations = get_registrations()
            if (student_id, course_id) in registrations:
                messagebox.showwarning("Registration", "Student is already registered for this course.")
                return
            
            # Register student
            register_student(student_id, course_id)
            
            # Refresh UI
            self.refresh_registration_tree()
            self.refresh_student_tree()
            self.refresh_course_tree()
            
            messagebox.showinfo("Success", "Student registered successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed:\n{str(e)}")
    
    def unregister_student(self) -> None:
        """
        Unregister the selected student from the selected course.
        
        Validates that both a student and course are selected, checks for
        existing registrations, and removes the registration relationship
        from the database.
        
        :raises Exception: If unregistration fails or validation errors occur.
        """
        student_text = self.reg_student_var.get()
        course_text = self.reg_course_var.get()
        
        if student_text == 'Select Student' or course_text == 'Select Course':
            messagebox.showwarning("Unregistration", "Please select both a student and a course.")
            return
        
        student_id = student_text.split(' - ')[0]
        course_id = course_text.split(' - ')[0]
        
        try:
            # Check if registered
            registrations = get_registrations()
            if (student_id, course_id) not in registrations:
                messagebox.showwarning("Unregistration", "Student is not registered for this course.")
                return
            
            # Unregister student
            unregister_student(student_id, course_id)
            
            # Refresh UI
            self.refresh_registration_tree()
            self.refresh_student_tree()
            self.refresh_course_tree()
            
            messagebox.showinfo("Success", "Student unregistered successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Unregistration failed:\n{str(e)}")
    
    def search_registrations(self, *args) -> None:
        """
        Search and filter registrations based on the provided query.
        
        Searches through student IDs, student names, course IDs, and course names
        for matches with the query string. Case-insensitive search that updates
        the TreeView to show only matching registrations.
        
        :param *args: Variable arguments (unused, for compatibility with Tkinter callbacks).
        """
        query = self.reg_search_var.get().strip().lower()
        
        # Clear tree
        for item in self.registration_tree.get_children():
            self.registration_tree.delete(item)
        
        registrations = get_registrations()
        students = {s[0]: s[1] for s in get_students()}
        courses = {c[0]: c[1] for c in get_courses()}
        
        for student_id, course_id in registrations:
            student_name = students.get(student_id, 'Unknown')
            course_name = courses.get(course_id, 'Unknown')
            
            if (query in student_id.lower() or query in student_name.lower() or 
                query in course_id.lower() or query in course_name.lower()):
                self.registration_tree.insert('', 'end', values=(student_id, student_name, course_id, course_name))

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolManagementApp(root)
    root.mainloop()
