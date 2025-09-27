"""
Person module providing the base Person class for the School Management System.

This module defines the foundational Person class that serves as the base
for both Student and Instructor classes. It includes email validation,
age constraints, and common person-related functionality.
"""

import re

class Person:
    """
    Base class representing a person in the school management system.
    
    This class provides common functionality for both students and instructors,
    including email validation, age constraints, and data serialization.
    
    :ivar name: The person's full name.
    :vartype name: str
    :ivar age: The person's age in years.
    :vartype age: int
    :ivar __email: The person's email address (private).
    :vartype __email: str
    """
    
    def __init__(self, name: str, age: int, email: str) -> None:
        """
        Initialize a Person instance with validation.
        
        :param name: The person's full name.
        :type name: str
        :param age: The person's age in years.
        :type age: int
        :param email: The person's email address.
        :type email: str
        :raises ValueError: If email format is invalid or age is out of range.
        """
        if not self._is_valid_email(email):
            raise ValueError("Invalid email format.")
        if age < 1:
            raise ValueError("Age must be at least 1 year old.")
        if age > 150:
            raise ValueError("Age must be no more than 150 years old.")
        self.name = name
        self.age = age
        self.__email = email  # private attribute

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """
        Validate email format using regex pattern.
        
        :param email: Email address to validate.
        :type email: str
        :return: True if email format is valid, False otherwise.
        :rtype: bool
        """
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None

    def introduce(self) -> None:
        """
        Print a friendly introduction message.
        
        Displays the person's name and age in a conversational format.
        """
        print(f"Hey there its me, {self.name}, and I'm {self.age} years old.")

    def to_dict(self) -> dict:
        """
        Convert person data to dictionary format.
        
        :return: Dictionary containing person's name, age, and email.
        :rtype: dict
        """
        return {
            'name': self.name,
            'age': self.age,
            'email': self.__email
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Person':
        """
        Create Person instance from dictionary data.
        
        :param data: Dictionary containing name, age, and email keys.
        :type data: dict
        :return: New Person instance.
        :rtype: Person
        """
        return cls(data['name'], data['age'], data['email'])
