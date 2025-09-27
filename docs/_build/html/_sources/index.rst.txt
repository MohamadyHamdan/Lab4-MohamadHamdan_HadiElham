School Management System Documentation
=====================================

Welcome to the School Management System documentation! This system provides a comprehensive solution for managing students, instructors, courses, and registrations in an educational institution.

Features
--------

* **Student Management**: Add, edit, delete, and search students with full validation
* **Instructor Management**: Manage instructor information and course assignments
* **Course Management**: Create and manage courses with instructor assignments
* **Registration System**: Register students for courses and manage enrollments
* **Data Validation**: Comprehensive input validation with user-friendly error messages
* **Database Operations**: SQLite database with full CRUD operations
* **Data Import/Export**: JSON import/export functionality
* **Modern GUI**: PyQt5-based interface with tabbed navigation

Architecture
------------

The system is built using:

* **Frontend**: PyQt5 with tabbed interface
* **Backend**: SQLite database with Python SQLite3
* **Validation**: Custom validation framework with regex patterns
* **Data Format**: JSON for import/export operations
* **Error Handling**: Custom ValidationError exceptions

Getting Started
---------------

To run the School Management System:

1. Ensure Python 3.7+ is installed
2. Install required dependencies: ``pip install PyQt5``
3. Run the main application: ``python main_qt.py``

The system will automatically create the database and initialize all necessary tables.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
