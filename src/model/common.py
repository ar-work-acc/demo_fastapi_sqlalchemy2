"""
Common utility functions.
"""

import re
from typing import Any

from sqlalchemy.orm import validates


def is_email_valid(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True
    else:
        return False


class EmailValidatorMixin:
    @validates("email")
    def validate_email(self, key: Any, value: str) -> str:
        if not is_email_valid(value):
            raise ValueError("Email validation failed!")
        return value
