"""
Forms module providing Tkinter form components for the School Management System.

This module contains helper functions for creating consistent form elements
and UI components used throughout the Tkinter-based interface.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def get_course_list() -> list[tuple]:
    """
    Get dynamic course list from database.
    
    :return: List of tuples containing (course_id, course_name).
    :rtype: list[tuple]
    """
    try:
        from db import get_courses
        courses = get_courses()
        # Return as (course_id, course_name) tuples
        return [(course[0], course[1]) for course in courses]
    except:
        # Fallback to empty list if database not available
        return []

def create_student_form(parent, on_add_student):
    """Create a form for adding/editing students"""
    frame = ttk.Frame(parent)
    
    # Name field
    tk.Label(frame, text="Name:").grid(row=0, column=0, sticky='e')
    student_name_entry = tk.Entry(frame)
    student_name_entry.grid(row=0, column=1)
    
    # Age field
    tk.Label(frame, text="Age:").grid(row=1, column=0, sticky='e')
    student_age_entry = tk.Entry(frame)
    student_age_entry.grid(row=1, column=1)
    
    # Email field
    tk.Label(frame, text="Email:").grid(row=2, column=0, sticky='e')
    student_email_entry = tk.Entry(frame)
    student_email_entry.grid(row=2, column=1)
    
    # Student ID field
    tk.Label(frame, text="Student ID:").grid(row=3, column=0, sticky='e')
    student_id_entry = tk.Entry(frame)
    student_id_entry.grid(row=3, column=1)
    
    # Add button
    add_btn = tk.Button(frame, text="Add Student", command=lambda: on_add_student(
        student_name_entry.get(), student_age_entry.get(), student_email_entry.get(), student_id_entry.get()
    ))
    add_btn.grid(row=4, column=0, columnspan=2, pady=10)

    # Course registration section
    tk.Label(frame, text="Register for Course:").grid(row=5, column=0, sticky='e')
    course_list = get_course_list()
    course_names = [f"{cid} - {cname}" for cid, cname in course_list]
    course_var = tk.StringVar()
    course_dropdown = ttk.Combobox(frame, textvariable=course_var, values=course_names, state='readonly')
    course_dropdown.grid(row=5, column=1)
    tk.Button(frame, text="Register Course").grid(row=6, column=0, columnspan=2, pady=10)
    return frame, (student_name_entry, student_age_entry, student_email_entry, student_id_entry)

def create_instructor_form(parent, on_add_instructor):
    frame = ttk.Frame(parent)
    tk.Label(frame, text="Name:").grid(row=0, column=0, sticky='e')
    instructor_name_entry = tk.Entry(frame)
    instructor_name_entry.grid(row=0, column=1)
    tk.Label(frame, text="Age:").grid(row=1, column=0, sticky='e')
    instructor_age_entry = tk.Entry(frame)
    instructor_age_entry.grid(row=1, column=1)
    tk.Label(frame, text="Email:").grid(row=2, column=0, sticky='e')
    instructor_email_entry = tk.Entry(frame)
    instructor_email_entry.grid(row=2, column=1)
    tk.Label(frame, text="Instructor ID:").grid(row=3, column=0, sticky='e')
    instructor_id_entry = tk.Entry(frame)
    instructor_id_entry.grid(row=3, column=1)
    add_btn = tk.Button(frame, text="Add Instructor", command=lambda: on_add_instructor(
        instructor_name_entry.get(), instructor_age_entry.get(), instructor_email_entry.get(), instructor_id_entry.get()
    ))
    add_btn.grid(row=4, column=0, columnspan=2, pady=10)

    # Course assignment section
    tk.Label(frame, text="Assign to Course:").grid(row=5, column=0, sticky='e')
    course_list = get_course_list()
    course_names = [f"{cid} - {cname}" for cid, cname in course_list]
    course_var = tk.StringVar()
    course_dropdown = ttk.Combobox(frame, textvariable=course_var, values=course_names, state='readonly')
    course_dropdown.grid(row=5, column=1)
    tk.Button(frame, text="Assign Course").grid(row=6, column=0, columnspan=2, pady=10)
    return frame, (instructor_name_entry, instructor_age_entry, instructor_email_entry, instructor_id_entry)

def create_course_form(parent, on_add_course):
    frame = ttk.Frame(parent)
    tk.Label(frame, text="Course ID:").grid(row=0, column=0, sticky='e')
    course_id_entry = tk.Entry(frame)
    course_id_entry.grid(row=0, column=1)
    tk.Label(frame, text="Course Name:").grid(row=1, column=0, sticky='e')
    course_name_entry = tk.Entry(frame)
    course_name_entry.grid(row=1, column=1)
    tk.Label(frame, text="Instructor ID:").grid(row=2, column=0, sticky='e')
    course_instructor_entry = tk.Entry(frame)
    course_instructor_entry.grid(row=2, column=1)
    add_btn = tk.Button(frame, text="Add Course", command=lambda: on_add_course(
        course_id_entry.get(), course_name_entry.get(), course_instructor_entry.get()
    ))
    add_btn.grid(row=3, column=0, columnspan=2, pady=10)
    return frame, (course_id_entry, course_name_entry, course_instructor_entry)

def create_search_bar(parent, on_search):
    frame = ttk.Frame(parent)
    search_var = tk.StringVar()
    search_entry = tk.Entry(frame, textvariable=search_var)
    search_entry.pack(side=tk.LEFT, padx=5)
    search_button = tk.Button(frame, text="Search", command=lambda: on_search(search_var.get()))
    search_button.pack(side=tk.LEFT)
    return frame, search_var

def create_student_treeview(parent):
    columns = ("student_id", "name", "age", "email", "courses")
    tree = ttk.Treeview(parent, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col.replace('_', ' ').title())
        tree.column(col, width=100)
    return tree

def create_instructor_treeview(parent):
    columns = ("instructor_id", "name", "age", "email", "courses")
    tree = ttk.Treeview(parent, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col.replace('_', ' ').title())
        tree.column(col, width=100)
    return tree

def create_course_treeview(parent):
    columns = ("course_id", "course_name", "instructor", "students")
    tree = ttk.Treeview(parent, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col.replace('_', ' ').title())
        tree.column(col, width=120)
    return tree

def create_edit_delete_buttons(parent, on_edit, on_delete):
    frame = ttk.Frame(parent)
    edit_button = tk.Button(frame, text="Edit", command=on_edit)
    edit_button.pack(side=tk.LEFT, padx=5)
    delete_button = tk.Button(frame, text="Delete", command=on_delete)
    delete_button.pack(side=tk.LEFT, padx=5)
    return frame

def create_save_load_buttons(parent, on_save, on_load):
    frame = ttk.Frame(parent)
    save_button = tk.Button(frame, text="Save Data", command=on_save)
    save_button.pack(side=tk.LEFT, padx=5)
    load_button = tk.Button(frame, text="Load Data", command=on_load)
    load_button.pack(side=tk.LEFT, padx=5)
    return frame

