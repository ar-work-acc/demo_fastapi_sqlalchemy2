"""
Common utility functions.
"""

import re

from sqlalchemy.orm import validates


def is_email_valid(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True
    else:
        return False


class EmailValidatorMixin:
    @validates("email")
    def validate_email(self, key, value):
        if not is_email_valid(value):
            raise ValueError("Email validation failed!")
        return value
