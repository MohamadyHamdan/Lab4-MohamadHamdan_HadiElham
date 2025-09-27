# School Management System

A comprehensive school management system built with Python, featuring both Tkinter and PyQt5 graphical user interfaces. This project demonstrates object-oriented programming principles, database management, data validation, and modern GUI development.

## 🎯 Project Overview

This School Management System provides a complete solution for managing students, instructors, courses, and registrations in an educational institution. The system features two different GUI implementations using Tkinter and PyQt5, showcasing different approaches to desktop application development.

### Key Features

- **Dual GUI Implementation**: Both Tkinter and PyQt5 interfaces
- **Complete CRUD Operations**: Create, Read, Update, Delete for all entities
- **Data Validation**: Comprehensive input validation with user-friendly error messages
- **Database Management**: SQLite database with proper relationships
- **Search Functionality**: Real-time search across all data
- **Import/Export**: JSON data import and export capabilities
- **Database Backup**: Full database backup and restore functionality
- **Modern UI**: Professional, tabbed interface design

## 🏗️ Architecture

### Core Components

- **Person.py**: Base class for all people in the system
- **Student.py**: Student class inheriting from Person
- **Instructor.py**: Instructor class inheriting from Person  
- **Course.py**: Course management class
- **db.py**: Database operations and SQLite management
- **validation.py**: Comprehensive data validation framework
- **forms.py**: Tkinter form creation utilities

### GUI Implementations

- **main.py**: Tkinter-based GUI application
- **main_qt.py**: PyQt5-based GUI application

## 📋 Requirements

### System Requirements
- Python 3.7 or higher
- Windows, macOS, or Linux

### Python Dependencies
- **Built-in modules**: `tkinter`, `sqlite3`, `json`, `re`, `os`, `datetime`
- **External dependencies**: `PyQt5`

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd Lab4-MohamadHamdan_HadiElham
   ```

2. **Install PyQt5** (required for PyQt5 GUI)
   ```bash
   pip install PyQt5
   ```

3. **No additional setup required** - all other dependencies are built into Python

## 🚀 How to Run

### Option 1: Tkinter GUI (Recommended for beginners)

The Tkinter version uses Python's built-in GUI toolkit and requires no additional installations.

```bash
python main.py
```

**Features:**
- Lightweight and fast
- No external dependencies
- Cross-platform compatibility
- Professional tabbed interface

### Option 2: PyQt5 GUI (Modern interface)

The PyQt5 version provides a more modern and polished user interface.

```bash
python main_qt.py
```

**Features:**
- Modern, professional appearance
- Enhanced user experience
- Better styling and layout options
- More responsive interface

## 📖 User Guide

### Main Interface

Both GUIs feature a tabbed interface with four main sections:

1. **Students Tab**
   - Add, edit, delete students
   - Register students for courses
   - Search and filter student data
   - View student course registrations

2. **Instructors Tab**
   - Add, edit, delete instructors
   - Assign instructors to courses
   - Search and filter instructor data
   - View instructor course assignments

3. **Courses Tab**
   - Add, edit, delete courses
   - Assign instructors to courses
   - Search and filter course data
   - View enrolled students

4. **Registrations Tab**
   - Register/unregister students for courses
   - View all current registrations
   - Search registration data

### Data Management

- **Backup Database**: Create backups of your data
- **Save JSON**: Export all data to JSON format
- **Load JSON**: Import data from JSON files

### Data Validation

The system includes comprehensive validation for:
- **Names**: Letters, spaces, apostrophes, and hyphens only
- **Ages**: Must be between 1 and 150 years
- **Emails**: Valid email format required
- **IDs**: Alphanumeric characters, underscores, and hyphens
- **Duplicates**: Prevents duplicate IDs and emails

## 🗄️ Database Schema

The system uses SQLite with the following tables:

- **students**: Student information (ID, name, age, email)
- **instructors**: Instructor information (ID, name, age, email)
- **courses**: Course information (ID, name, instructor_id)
- **registrations**: Student-course relationships (student_id, course_id)

## 📁 Project Structure

```
Lab4-MohamadHamdan_HadiElham/
├── main.py                 # Tkinter GUI application
├── main_qt.py             # PyQt5 GUI application
├── Person.py              # Base Person class
├── Student.py             # Student class
├── Instructor.py          # Instructor class
├── Course.py              # Course class
├── db.py                  # Database operations
├── validation.py          # Data validation
├── forms.py               # Tkinter form utilities
├── school.db              # SQLite database
├── school_data.json       # Sample data export
├── docs/                  # Documentation
└── README.md              # This file
```

## 🔧 Development Features

### Object-Oriented Design
- Inheritance hierarchy (Person → Student/Instructor)
- Encapsulation with private attributes
- Polymorphism through method overriding
- Data serialization methods

### Error Handling
- Custom ValidationError exceptions
- User-friendly error messages
- Graceful failure handling
- Input sanitization

### Code Quality
- Comprehensive docstrings
- Type hints throughout
- Modular design
- Clean separation of concerns

## 🎨 GUI Comparison

| Feature | Tkinter | PyQt5 |
|---------|---------|-------|
| Dependencies | Built-in | External |
| Performance | Fast | Fast |
| Styling | Basic | Advanced |
| Learning Curve | Easy | Moderate |
| Cross-platform | Yes | Yes |
| File Size | Small | Larger |

## 🐛 Troubleshooting

### Common Issues

1. **PyQt5 not found**
   ```bash
   pip install PyQt5
   ```

2. **Database errors**
   - Ensure write permissions in the project directory
   - Check if school.db file is not locked by another process

3. **Import errors**
   - Ensure all Python files are in the same directory
   - Check Python version compatibility

### Getting Help

- Check the console output for error messages
- Ensure all required files are present
- Verify Python version (3.7+)

## 📝 Sample Data

The project includes a sample `school_data.json` file with example data that can be imported to test the system functionality.

## 🏆 Project Highlights

- **Dual GUI Implementation**: Demonstrates both Tkinter and PyQt5
- **Professional Documentation**: Comprehensive docstrings and comments
- **Data Integrity**: Robust validation and error handling
- **Modern Design**: Clean, intuitive user interface
- **Scalable Architecture**: Easy to extend and modify
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 👥 Authors

- **Hadi Elham** - Lead Developer
- **Mohamad Hamdan** - Project Collaborator

## 📄 License

This project is created for educational purposes as part of Lab 4 coursework.

---

**Ready to get started?** Choose your preferred interface and run either `python main.py` (Tkinter) or `python main_qt.py` (PyQt5) to begin managing your school data!
