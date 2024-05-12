import logging

from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

import repository.employee as employee_repo
from core.auth import verify_password
from core.config import PROJECT_SETTINGS
from model import Employee

logger = logging.getLogger(__name__)


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
) -> Employee | bool:
    """
    Authenticate a user by checking their username and password against the
    employee records in the database.

    Parameters:
        session (AsyncSession): The database session to use for the
        authentication process.
        username (str): The username (email) of the user (employee).
        password (str): The password of the user (employee).

    Returns:
        Union[Employee, bool]: If the authentication is successful,
        returns the corresponding Employee object.
        If the authentication fails, returns False.
    """
    logger.debug(f"Authenticating user: {username}")

    employee = await employee_repo.get_employee_by_email(session, username)

    if employee is None:
        return False

    if not verify_password(password, employee.password_hash):
        return False

    return employee


def check_is_manager(token: str) -> bool:
    token_dict = jwt.decode(
        token,
        PROJECT_SETTINGS.JWT_SECRET_KEY,
        algorithms=[PROJECT_SETTINGS.JWT_ALGORITHM],
    )
    is_manager: bool = token_dict["is_manager"]

    return is_manager
