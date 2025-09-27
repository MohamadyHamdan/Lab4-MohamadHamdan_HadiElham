"""
Student module providing the Student class for the School Management System.

This module defines the Student class which inherits from Person and adds
student-specific functionality including course registration management
and data serialization capabilities.
"""

from Person import Person
import json

class Student(Person):
    """
    Student class representing a student in the school management system.
    
    Inherits from Person and adds student-specific functionality including
    course registration management and student ID tracking.
    
    :ivar student_id: Unique identifier for the student.
    :vartype student_id: str
    :ivar registered_courses: List of Course objects the student is registered for.
    :vartype registered_courses: list[Course]
    """
    
    def __init__(self, name: str, age: int, email: str, student_id: str) -> None:
        """
        Initialize a Student instance.
        
        :param name: The student's full name.
        :type name: str
        :param age: The student's age in years.
        :type age: int
        :param email: The student's email address.
        :type email: str
        :param student_id: Unique identifier for the student.
        :type student_id: str
        :raises ValueError: If email format is invalid or age is out of range.
        """
        super().__init__(name, age, email)
        self.student_id = student_id
        self.registered_courses = []  # list of 'Course' objects

    def register_course(self, course: "Course") -> None:
        """
        Register the student for a course.
        
        Adds the course to the student's registered courses list if not already registered.
        
        :param course: Course object to register for.
        :type course: Course
        """
        if course not in self.registered_courses:
            self.registered_courses.append(course)

    def to_dict(self) -> dict:
        """
        Convert student data to dictionary format.
        
        :return: Dictionary containing student's personal info and registered course IDs.
        :rtype: dict
        """
        return {
            'name': self.name,
            'age': self.age,
            'email': self._Person__email,
            'student_id': self.student_id,
            'registered_courses': [course.course_id for course in self.registered_courses]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        """
        Create Student instance from dictionary data.
        
        :param data: Dictionary containing student information.
        :type data: dict
        :return: New Student instance.
        :rtype: Student
        """
        student = cls(data['name'], data['age'], data['email'], data['student_id'])
        # registered_courses should be set after loading all courses
        return student

    @staticmethod
    def save_to_file(students: list['Student'], filename: str) -> None:
        """
        Save a list of students to a JSON file.
        
        :param students: List of Student objects to save.
        :type students: list[Student]
        :param filename: Path to the output JSON file.
        :type filename: str
        :raises IOError: If file cannot be written.
        """
        with open(filename, 'w') as f:
            json.dump([s.to_dict() for s in students], f)

    @staticmethod
    def load_from_file(filename: str) -> list['Student']:
        """
        Load students from a JSON file.
        
        :param filename: Path to the input JSON file.
        :type filename: str
        :return: List of Student objects loaded from file.
        :rtype: list[Student]
        :raises IOError: If file cannot be read.
        :raises json.JSONDecodeError: If file contains invalid JSON.
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        return [Student.from_dict(d) for d in data]
