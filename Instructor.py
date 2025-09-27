"""
Instructor module providing the Instructor class for the School Management System.

This module defines the Instructor class which inherits from Person and adds
instructor-specific functionality including course assignment management
and data serialization capabilities.
"""

from Person import Person
import json

class Instructor(Person):
    """
    Instructor class representing an instructor in the school management system.
    
    Inherits from Person and adds instructor-specific functionality including
    course assignment management and instructor ID tracking.
    
    :ivar instructor_id: Unique identifier for the instructor.
    :vartype instructor_id: str
    :ivar assigned_courses: List of Course objects the instructor is assigned to teach.
    :vartype assigned_courses: list[Course]
    """
    
    def __init__(self, name: str, age: int, email: str, instructor_id: str) -> None:
        """
        Initialize an Instructor instance.
        
        :param name: The instructor's full name.
        :type name: str
        :param age: The instructor's age in years.
        :type age: int
        :param email: The instructor's email address.
        :type email: str
        :param instructor_id: Unique identifier for the instructor.
        :type instructor_id: str
        :raises ValueError: If email format is invalid or age is out of range.
        """
        super().__init__(name, age, email)
        self.instructor_id = instructor_id
        self.assigned_courses = []  # list of 'Course' objects

    def assign_course(self, course: "Course") -> None:
        """
        Assign a course to the instructor.
        
        Adds the course to the instructor's assigned courses list if not already assigned.
        
        :param course: Course object to assign to the instructor.
        :type course: Course
        """
        if course not in self.assigned_courses:
            self.assigned_courses.append(course)

    def to_dict(self) -> dict:
        """
        Convert instructor data to dictionary format.
        
        :return: Dictionary containing instructor's personal info and assigned course IDs.
        :rtype: dict
        """
        return {
            'name': self.name,
            'age': self.age,
            'email': self._Person__email,
            'instructor_id': self.instructor_id,
            'assigned_courses': [course.course_id for course in self.assigned_courses]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Instructor':
        """
        Create Instructor instance from dictionary data.
        
        :param data: Dictionary containing instructor information.
        :type data: dict
        :return: New Instructor instance.
        :rtype: Instructor
        """
        instructor = cls(data['name'], data['age'], data['email'], data['instructor_id'])
        # assigned_courses should be set after loading all courses
        return instructor

    @staticmethod
    def save_to_file(instructors: list['Instructor'], filename: str) -> None:
        """
        Save a list of instructors to a JSON file.
        
        :param instructors: List of Instructor objects to save.
        :type instructors: list[Instructor]
        :param filename: Path to the output JSON file.
        :type filename: str
        :raises IOError: If file cannot be written.
        """
        with open(filename, 'w') as f:
            json.dump([i.to_dict() for i in instructors], f)

    @staticmethod
    def load_from_file(filename: str) -> list['Instructor']:
        """
        Load instructors from a JSON file.
        
        :param filename: Path to the input JSON file.
        :type filename: str
        :return: List of Instructor objects loaded from file.
        :rtype: list[Instructor]
        :raises IOError: If file cannot be read.
        :raises json.JSONDecodeError: If file contains invalid JSON.
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        return [Instructor.from_dict(d) for d in data]
