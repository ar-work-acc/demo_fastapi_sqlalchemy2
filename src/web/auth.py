from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from starlette import status

import service.auth as auth_service
from core.auth import create_access_token
from core.config import PROJECT_SETTINGS
from core.dependency import AsyncSessionDep, CurrentUserDep, TokenDep
from model.employee import Employee
from schema.employee import EmployeeBase
from schema.token import Token

router = APIRouter()


@router.post("/login")
async def login(
    session: AsyncSessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """This is the main authentication endpoint.

    Args:
        session (Annotated[AsyncSession, Depends): The session object.
        form_data (Annotated[OAuth2PasswordRequestForm, Depends): This includes
        the username and password as form data.

    Raises:
        HTTPException: If username or password is incorrect.

    Returns:
        Token: The bearer access token.
    """
    user = await auth_service.authenticate_user(
        session,
        form_data.username,
        form_data.password,
    )
    if not user:
        # authentication failed, raise an exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if isinstance(user, Employee):
        # authentication successful, create an access token
        access_token_expires = timedelta(
            minutes=PROJECT_SETTINGS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        access_token = create_access_token(
            user,
            expires_delta=access_token_expires,
        )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/employee-info", response_model=EmployeeBase)
async def get_employee_info(
    employee: CurrentUserDep,
) -> Employee:
    """For a logged in user with a JWT token, query the database
    for employee info.

    Args:
        employee (Annotated[Employee, Depends): The target SQLAlchemy
        employee model.

    Returns:
        Employee (converted to EmployeeBase): The employee Pydantic model.
    """
    return employee


@router.get("/user-info")
async def get_user_info(
    token: TokenDep,
) -> dict[str, Any]:
    """Get user info by decoding the JWT token
    (although probably not necessary).

    Args:
        token (Annotated[str, Depends): The JWT token from the client.

    Returns:
        dict: The decoded JWT token.
    """
    return jwt.decode(
        token,
        PROJECT_SETTINGS.JWT_SECRET_KEY,
        algorithms=[PROJECT_SETTINGS.JWT_ALGORITHM],
    )
