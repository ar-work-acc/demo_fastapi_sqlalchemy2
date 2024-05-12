"""
For dependency injection.
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

import repository.employee as employee_repo
import service.auth as auth_service
from core.config import PROJECT_SETTINGS
from model import AsyncSessionMaker, Employee


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionMaker() as session:
        yield session


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{PROJECT_SETTINGS.API_V1_PATH}auth/login",
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Employee:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            PROJECT_SETTINGS.JWT_SECRET_KEY,
            algorithms=[PROJECT_SETTINGS.JWT_ALGORITHM],
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await employee_repo.get_employee_by_email(session, username)
    if user is None:
        raise credentials_exception
    return user


def check_logged_in_user_is_manager(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> bool:
    """This DI function checks if the user is a manager; if not, raises an
    exception.

    Args:
        token (Annotated[str, Depends): the JWT token

    Raises:
        HTTPException: if the user is not a manager

    Returns:
        bool: True if the user is a manager
    """
    result = auth_service.check_is_manager(token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized. Only managers can access this endpoint.",
        )

    return result


# define DI re-usable types:
AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
CurrentUserDep = Annotated[Employee, Depends(get_current_user)]
IsManagerDep = Annotated[bool, Depends(check_logged_in_user_is_manager)]
