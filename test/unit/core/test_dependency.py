from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from core.auth import create_access_token
from core.config import PROJECT_SETTINGS
from core.dependency import get_current_user
from model.employee import Employee
from schema.user import User


async def test_get_current_user_without_token(session):
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user("", session)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate credentials"
    assert excinfo.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.parametrize("username", ["", "non-existing-username"])
async def test_get_current_user_with_nonexistent_user_name(username, session):
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
        session,
        monkeypatch,
):
    # use mocking to test such a situation
    def mock_decode(*args, **kwargs):
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
