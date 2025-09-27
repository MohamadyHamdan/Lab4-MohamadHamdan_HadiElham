"""
Validation module providing comprehensive data validation for the School Management System.

This module contains the DataValidator class and ValidationError exception for
validating all input data including names, ages, emails, IDs, and checking for
duplicates in the database.
"""

import re
import sqlite3
from typing import Optional, List, Tuple
from db import get_connection

# Custom exception for handling validation errors
class ValidationError(Exception):
    """
    Custom exception raised when data validation fails.
    
    :ivar message: Error message describing the validation failure.
    :vartype message: str
    :ivar field: Name of the field that failed validation.
    :vartype field: str, optional
    """
    
    def __init__(self, message: str, field: str = None) -> None:
        """
        Initialize ValidationError with message and optional field.
        
        :param message: Error message describing the validation failure.
        :type message: str
        :param field: Name of the field that failed validation.
        :type field: str, optional
        """
        self.message = message
        self.field = field
        super().__init__(self.message)

class DataValidator:
    """
    Comprehensive data validator for the School Management System.
    
    Provides static methods for validating names, ages, emails, IDs, and checking
    for duplicates in the database. Uses regex patterns and database queries to
    ensure data integrity and consistency.
    
    :cvar MIN_AGE: Minimum allowed age.
    :vartype MIN_AGE: int
    :cvar MAX_AGE: Maximum allowed age.
    :vartype MAX_AGE: int
    :cvar MIN_NAME_LENGTH: Minimum name length.
    :vartype MIN_NAME_LENGTH: int
    :cvar MAX_NAME_LENGTH: Maximum name length.
    :vartype MAX_NAME_LENGTH: int
    :cvar MIN_ID_LENGTH: Minimum ID length.
    :vartype MIN_ID_LENGTH: int
    :cvar MAX_ID_LENGTH: Maximum ID length.
    :vartype MAX_ID_LENGTH: int
    :cvar MIN_EMAIL_LENGTH: Minimum email length.
    :vartype MIN_EMAIL_LENGTH: int
    :cvar MAX_EMAIL_LENGTH: Maximum email length.
    :vartype MAX_EMAIL_LENGTH: int
    :cvar EMAIL_REGEX: Regex pattern for email validation.
    :vartype EMAIL_REGEX: str
    :cvar ID_REGEX: Regex pattern for ID validation.
    :vartype ID_REGEX: str
    :cvar NAME_REGEX: Regex pattern for name validation.
    :vartype NAME_REGEX: str
    """
    
    # Validation constants - keeping these reasonable
    MIN_AGE = 1
    MAX_AGE = 150
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 100
    MIN_ID_LENGTH = 3
    MAX_ID_LENGTH = 20
    MIN_EMAIL_LENGTH = 5
    MAX_EMAIL_LENGTH = 254
    
    # Regex patterns for validation
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    ID_REGEX = r"^[a-zA-Z0-9_-]+$"  # Only alphanumeric, underscore, and hyphen
    NAME_REGEX = r"^[a-zA-Z\s'-]+$"  # Letters, spaces, apostrophes, and hyphens
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email format and return cleaned email.
        
        :param email: Email address to validate.
        :type email: str
        :return: Validated and cleaned email in lowercase.
        :rtype: str
        :raises ValidationError: If email is empty, too short, too long, or invalid format.
        """
        # Check if email is provided
        if not email:
            raise ValidationError("Email is required", "email")
        
        # Clean up the email
        email = email.strip()
        
        # Check length constraints
        if len(email) < DataValidator.MIN_EMAIL_LENGTH:
            raise ValidationError(f"Email must be at least {DataValidator.MIN_EMAIL_LENGTH} characters", "email")
        
        if len(email) > DataValidator.MAX_EMAIL_LENGTH:
            raise ValidationError(f"Email must be no more than {DataValidator.MAX_EMAIL_LENGTH} characters", "email")
        
        # Validate email format using regex
        if not re.match(DataValidator.EMAIL_REGEX, email):
            raise ValidationError("Invalid email format. Please use format: user@domain.com", "email")
        
        # Return lowercase email for consistency
        return email.lower()
    
    @staticmethod
    def validate_age(age: str) -> int:
        """
        Validate age and return as integer.
        
        :param age: Age as string to validate.
        :type age: str
        :return: Validated age as integer.
        :rtype: int
        :raises ValidationError: If age is empty, not a number, or out of range.
        """
        # Make sure age is provided
        if not age:
            raise ValidationError("Age is required", "age")
        
        # Clean up the input
        age = age.strip()
        
        # Convert to integer
        try:
            age_int = int(age)
        except ValueError:
            raise ValidationError("Age must be a valid number", "age")
        
        # Check age bounds
        if age_int < DataValidator.MIN_AGE:
            raise ValidationError(f"Age must be at least {DataValidator.MIN_AGE} year old", "age")
        
        if age_int > DataValidator.MAX_AGE:
            raise ValidationError(f"Age must be no more than {DataValidator.MAX_AGE}", "age")
        
        return age_int
    
    @staticmethod
    def validate_name(name: str) -> str:
        """
        Validate name format and return cleaned name.
        
        :param name: Name to validate.
        :type name: str
        :return: Validated and cleaned name with proper capitalization.
        :rtype: str
        :raises ValidationError: If name is empty, too short, too long, or invalid format.
        """
        if not name:
            raise ValidationError("Name is required", "name")
        
        name = name.strip()
        
        if len(name) < DataValidator.MIN_NAME_LENGTH:
            raise ValidationError(f"Name must be at least {DataValidator.MIN_NAME_LENGTH} characters", "name")
        
        if len(name) > DataValidator.MAX_NAME_LENGTH:
            raise ValidationError(f"Name must be no more than {DataValidator.MAX_NAME_LENGTH} characters", "name")
        
        if not re.match(DataValidator.NAME_REGEX, name):
            raise ValidationError("Name can only contain letters, spaces, apostrophes, and hyphens", "name")
        
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in name.split())
    
    @staticmethod
    def validate_id(id_value: str, id_type: str = "ID") -> str:
        """
        Validate ID format and return cleaned ID.
        
        :param id_value: ID value to validate.
        :type id_value: str
        :param id_type: Type of ID for error messages, defaults to "ID".
        :type id_type: str, optional
        :return: Validated and cleaned ID in uppercase.
        :rtype: str
        :raises ValidationError: If ID is empty, too short, too long, or invalid format.
        """
        if not id_value:
            raise ValidationError(f"{id_type} is required", "id")
        
        id_value = id_value.strip()
        
        if len(id_value) < DataValidator.MIN_ID_LENGTH:
            raise ValidationError(f"{id_type} must be at least {DataValidator.MIN_ID_LENGTH} characters", "id")
        
        if len(id_value) > DataValidator.MAX_ID_LENGTH:
            raise ValidationError(f"{id_type} must be no more than {DataValidator.MAX_ID_LENGTH} characters", "id")
        
        if not re.match(DataValidator.ID_REGEX, id_value):
            raise ValidationError(f"{id_type} can only contain letters, numbers, underscores, and hyphens", "id")
        
        return id_value.upper()
    
    @staticmethod
    def check_student_id_exists(student_id: str, exclude_id: str = None) -> bool:
        """Check if student ID already exists in database"""
        with get_connection() as conn:
            c = conn.cursor()
            if exclude_id:
                c.execute("SELECT COUNT(*) FROM students WHERE student_id = ? AND student_id != ?", 
                         (student_id, exclude_id))
            else:
                c.execute("SELECT COUNT(*) FROM students WHERE student_id = ?", (student_id,))
            return c.fetchone()[0] > 0
    
    @staticmethod
    def check_instructor_id_exists(instructor_id: str, exclude_id: str = None) -> bool:
        """Check if instructor ID already exists in database"""
        with get_connection() as conn:
            c = conn.cursor()
            if exclude_id:
                c.execute("SELECT COUNT(*) FROM instructors WHERE instructor_id = ? AND instructor_id != ?", 
                         (instructor_id, exclude_id))
            else:
                c.execute("SELECT COUNT(*) FROM instructors WHERE instructor_id = ?", (instructor_id,))
            return c.fetchone()[0] > 0
    
    @staticmethod
    def check_course_id_exists(course_id: str, exclude_id: str = None) -> bool:
        """Check if course ID already exists in database"""
        with get_connection() as conn:
            c = conn.cursor()
            if exclude_id:
                c.execute("SELECT COUNT(*) FROM courses WHERE course_id = ? AND course_id != ?", 
                         (course_id, exclude_id))
            else:
                c.execute("SELECT COUNT(*) FROM courses WHERE course_id = ?", (course_id,))
            return c.fetchone()[0] > 0
    
    @staticmethod
    def check_instructor_exists(instructor_id: str) -> bool:
        """Check if instructor exists in database"""
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM instructors WHERE instructor_id = ?", (instructor_id,))
            return c.fetchone()[0] > 0
    
    @staticmethod
    def check_email_exists(email: str, table: str, exclude_id: str = None) -> bool:
        """Check if email already exists in specified table"""
        with get_connection() as conn:
            c = conn.cursor()
            if exclude_id:
                id_field = "student_id" if table == "students" else "instructor_id"
                c.execute(f"SELECT COUNT(*) FROM {table} WHERE email = ? AND {id_field} != ?", 
                         (email, exclude_id))
            else:
                c.execute(f"SELECT COUNT(*) FROM {table} WHERE email = ?", (email,))
            return c.fetchone()[0] > 0
    
    @staticmethod
    def validate_student_data(name: str, age: str, email: str, student_id: str, 
                            is_edit: bool = False, exclude_id: str = None) -> Tuple[str, int, str, str]:
        """
        Validate all student data and return cleaned values.
        
        :param name: Student's name to validate.
        :type name: str
        :param age: Student's age to validate.
        :type age: str
        :param email: Student's email to validate.
        :type email: str
        :param student_id: Student's ID to validate.
        :type student_id: str
        :param is_edit: Whether this is an edit operation, defaults to False.
        :type is_edit: bool, optional
        :param exclude_id: ID to exclude from duplicate checks, defaults to None.
        :type exclude_id: str, optional
        :return: Tuple of (validated_name, validated_age, validated_email, validated_id).
        :rtype: Tuple[str, int, str, str]
        :raises ValidationError: If any validation fails or duplicates are found.
        """
        errors = []
        
        try:
            validated_name = DataValidator.validate_name(name)
        except ValidationError as e:
            errors.append(e.message)
        
        try:
            validated_age = DataValidator.validate_age(age)
        except ValidationError as e:
            errors.append(e.message)
        
        try:
            validated_email = DataValidator.validate_email(email)
        except ValidationError as e:
            errors.append(e.message)
        
        try:
            validated_id = DataValidator.validate_id(student_id, "Student ID")
        except ValidationError as e:
            errors.append(e.message)
        
        # Check for duplicates only if validation passed
        if not errors:
            if DataValidator.check_student_id_exists(validated_id, exclude_id):
                errors.append("Student ID already exists")
            
            if DataValidator.check_email_exists(validated_email, "students", exclude_id):
                errors.append("Email already exists for another student")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return validated_name, validated_age, validated_email, validated_id
    
    @staticmethod
    def validate_instructor_data(name: str, age: str, email: str, instructor_id: str, 
                               is_edit: bool = False, exclude_id: str = None) -> Tuple[str, int, str, str]:
        """Validate all instructor data and return cleaned values"""
        errors = []
        
        try:
            validated_name = DataValidator.validate_name(name)
        except ValidationError as e:
            errors.append(e.message)
        
        try:
            validated_age = DataValidator.validate_age(age)
        except ValidationError as e:
            errors.append(e.message)
        
        try:
            validated_email = DataValidator.validate_email(email)
        except ValidationError as e:
            errors.append(e.message)
        
        try:
            validated_id = DataValidator.validate_id(instructor_id, "Instructor ID")
        except ValidationError as e:
            errors.append(e.message)
        
        # Check for duplicates only if validation passed
        if not errors:
            if DataValidator.check_instructor_id_exists(validated_id, exclude_id):
                errors.append("Instructor ID already exists")
            
            if DataValidator.check_email_exists(validated_email, "instructors", exclude_id):
                errors.append("Email already exists for another instructor")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return validated_name, validated_age, validated_email, validated_id
    
    @staticmethod
    def validate_course_data(course_id: str, course_name: str, instructor_id: str = None, exclude_id: str = None) -> Tuple[str, str, str]:
        """Validate course data and return cleaned values"""
        errors = []
        
        try:
            validated_id = DataValidator.validate_id(course_id, "Course ID")
        except ValidationError as e:
            errors.append(e.message)
        
        try:
            validated_name = DataValidator.validate_name(course_name)
        except ValidationError as e:
            errors.append(e.message)
        
        # Validate instructor ID if provided
        validated_instructor_id = None
        if instructor_id and instructor_id.strip() != '':
            try:
                validated_instructor_id = DataValidator.validate_id(instructor_id.strip(), "Instructor ID")
                # Check if instructor exists
                if not DataValidator.check_instructor_exists(validated_instructor_id):
                    errors.append("Selected instructor does not exist")
            except ValidationError as e:
                errors.append(f"Instructor validation failed: {e.message}")
        
        # Check for duplicates only if validation passed
        if not errors:
            if DataValidator.check_course_id_exists(validated_id, exclude_id):
                errors.append("Course ID already exists")
        
        if errors:
            raise ValidationError("; ".join(errors))
        
        return validated_id, validated_name, validated_instructor_id

# Convenience functions for backward compatibility
def is_valid_email(email: str) -> bool:
    """Legacy function for email validation"""
    try:
        DataValidator.validate_email(email)
        return True
    except ValidationError:
        return False

def is_non_negative_int(val: str) -> bool:
    """Legacy function for age validation"""
    try:
        DataValidator.validate_age(val)
        return True
    except ValidationError:
        return False
