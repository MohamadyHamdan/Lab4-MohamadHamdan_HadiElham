"""
Course module providing the Course class for the School Management System.

This module defines the Course class which manages course information,
instructor assignments, student enrollments, and data serialization.
"""

import json

class Course:
    """
    Course class representing a course in the school management system.
    
    Manages course information, instructor assignments, and student enrollments.
    Provides functionality for adding students and serializing course data.
    
    :ivar course_id: Unique identifier for the course.
    :vartype course_id: str
    :ivar course_name: Name of the course.
    :vartype course_name: str
    :ivar instructor: Instructor object assigned to teach the course.
    :vartype instructor: Instructor or None
    :ivar enrolled_students: List of Student objects enrolled in the course.
    :vartype enrolled_students: list[Student]
    """
    
    def __init__(self, course_id: str, course_name: str, instructor: "Instructor" = None) -> None:
        """
        Initialize a Course instance.
        
        :param course_id: Unique identifier for the course.
        :type course_id: str
        :param course_name: Name of the course.
        :type course_name: str
        :param instructor: Instructor assigned to teach the course, defaults to None.
        :type instructor: Instructor, optional
        """
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        self.enrolled_students = []  # list of 'Student' objects

    def add_student(self, student: "Student") -> None:
        """
        Add a student to the course enrollment.
        
        Adds the student to the enrolled students list if not already enrolled.
        
        :param student: Student object to add to the course.
        :type student: Student
        """
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)

    def to_dict(self) -> dict:
        """
        Convert course data to dictionary format.
        
        :return: Dictionary containing course info, instructor ID, and enrolled student IDs.
        :rtype: dict
        """
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'instructor_id': self.instructor.instructor_id if self.instructor else None,
            'enrolled_students': [s.student_id for s in self.enrolled_students]
        }

    @classmethod
    def from_dict(cls, data: dict, instructor_lookup: dict = None, student_lookup: dict = None) -> 'Course':
        """
        Create Course instance from dictionary data.
        
        :param data: Dictionary containing course information.
        :type data: dict
        :param instructor_lookup: Dictionary mapping instructor IDs to Instructor objects.
        :type instructor_lookup: dict, optional
        :param student_lookup: Dictionary mapping student IDs to Student objects.
        :type student_lookup: dict, optional
        :return: New Course instance.
        :rtype: Course
        """
        instructor = instructor_lookup[data['instructor_id']] if instructor_lookup and data['instructor_id'] else None
        course = cls(data['course_id'], data['course_name'], instructor)
        if student_lookup:
            course.enrolled_students = [student_lookup[sid] for sid in data['enrolled_students'] if sid in student_lookup]
        return course

    @staticmethod
    def save_to_file(courses: list['Course'], filename: str) -> None:
        """
        Save a list of courses to a JSON file.
        
        :param courses: List of Course objects to save.
        :type courses: list[Course]
        :param filename: Path to the output JSON file.
        :type filename: str
        :raises IOError: If file cannot be written.
        """
        with open(filename, 'w') as f:
            json.dump([c.to_dict() for c in courses], f)

    @staticmethod
    def load_from_file(filename: str, instructor_lookup: dict = None, student_lookup: dict = None) -> list['Course']:
        """
        Load courses from a JSON file.
        
        :param filename: Path to the input JSON file.
        :type filename: str
        :param instructor_lookup: Dictionary mapping instructor IDs to Instructor objects.
        :type instructor_lookup: dict, optional
        :param student_lookup: Dictionary mapping student IDs to Student objects.
        :type student_lookup: dict, optional
        :return: List of Course objects loaded from file.
        :rtype: list[Course]
        :raises IOError: If file cannot be read.
        :raises json.JSONDecodeError: If file contains invalid JSON.
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        return [Course.from_dict(d, instructor_lookup, student_lookup) for d in data]
