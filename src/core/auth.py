from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from core.config import PROJECT_SETTINGS
from model import Employee
from schema.user import User


def get_password_hash(password: str) -> str:
    """
    Generates a bcrypt hash for the given password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The bcrypt hash of the password.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies whether the provided password matches the given bcrypt hash.

    Args:
        password (str): The password to verify.
        hashed_password (str): The bcrypt hash to compare against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    employee: Employee,
    expires_delta: timedelta | None = None,
):
    user = User(
        sub=employee.email,
        first_name=employee.first_name,
        last_name=employee.last_name,
        exp=datetime.now(timezone.utc),
        is_manager=employee.is_manager,
    )

    if expires_delta:
        user.exp += expires_delta
    else:
        user.exp += timedelta(minutes=15)

    User.model_validate(user)

    encoded_jwt = jwt.encode(
        user.model_dump(),
        PROJECT_SETTINGS.JWT_SECRET_KEY,
        algorithm=PROJECT_SETTINGS.JWT_ALGORITHM,
    )

    return encoded_jwt
