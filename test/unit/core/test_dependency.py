from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi import HTTPException
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import PROJECT_SETTINGS
from core.dependency import get_current_user
from schema.user import User


async def test_get_current_user_without_token(session: AsyncSession) -> None:
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user("", session)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"
    assert excinfo.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.parametrize("username", ["", "non-existing-username"])
async def test_get_current_user_with_nonexistent_user_name(
    username: str,
    session: AsyncSession,
) -> None:
    user = User(
        sub=username,
        first_name="Test",
        last_name="",
        exp=datetime.now(timezone.utc),
        is_manager=False,
    )
    token = jwt.encode(
        user.model_dump(),
        PROJECT_SETTINGS.JWT_SECRET_KEY,
        algorithm=PROJECT_SETTINGS.JWT_ALGORITHM,
    )
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token, session)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"
    assert excinfo.value.headers == {"WWW-Authenticate": "Bearer"}


async def test_get_current_user_with_username_equaling_none(
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # use mocking to test such a situation
    def mock_decode(*args: Any, **kwargs: Any) -> dict[str, None]:
        return {"sub": None}

    monkeypatch.setattr(
        jwt,
        "decode",
        mock_decode,
    )

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user("", session)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"
    assert excinfo.value.headers == {"WWW-Authenticate": "Bearer"}
