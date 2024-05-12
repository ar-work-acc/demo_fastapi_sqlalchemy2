import logging

from httpx import AsyncClient

from core.config import PROJECT_SETTINGS
from main import app

from .conftest import BASE_URL

logger = logging.getLogger(__name__)


async def test_root(async_client: AsyncClient) -> None:
    response = await async_client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "FastAPI + SQLAlchemy 2.0 Demo Project"
    }


async def test_admin_login() -> None:
    form_data = {
        "username": PROJECT_SETTINGS.ADMIN_USERNAME,
        "password": PROJECT_SETTINGS.ADMIN_PASSWORD,
    }
    async with AsyncClient(
        app=app,
        base_url=BASE_URL,
    ) as ac:
        response = await ac.post("/api/v1/auth/login", data=form_data)

    assert response.status_code == 200

    json_result = response.json()
    assert json_result["token_type"] == "bearer"
    assert "access_token" in json_result


async def test_user_login() -> None:
    form_data = {
        "username": PROJECT_SETTINGS.USER_USERNAME,
        "password": PROJECT_SETTINGS.USER_PASSWORD,
    }
    async with AsyncClient(
        app=app,
        base_url=BASE_URL,
    ) as ac:
        response = await ac.post("/api/v1/auth/login", data=form_data)

    assert response.status_code == 200

    json_result = response.json()
    assert json_result["token_type"] == "bearer"
    assert "access_token" in json_result


async def test_user_login_failure() -> None:
    form_data = {
        "username": PROJECT_SETTINGS.USER_USERNAME,
        "password": "x",
    }
    async with AsyncClient(
        app=app,
        base_url=BASE_URL,
    ) as ac:
        response = await ac.post("/api/v1/auth/login", data=form_data)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect username or password"
    }


async def test_unknown_user_login_failure() -> None:
    form_data = {
        "username": "unknown",
        "password": "x",
    }
    async with AsyncClient(
        app=app,
        base_url=BASE_URL,
    ) as ac:
        response = await ac.post("/api/v1/auth/login", data=form_data)

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Incorrect username or password"
    }


async def test_get_employee_info(
        async_client: AsyncClient,
        auth_header_user: dict[str, str],
) -> None:
    response = await async_client.get(
        "/api/v1/auth/employee-info",
        headers=auth_header_user,
    )

    assert response.status_code == 200
    assert response.json() == {
        "employee_id": 2,
        "email": "alice@meowfish.org",
        "first_name": "Alice",
        "last_name": "Maxwell",
        "is_manager": False
    }


async def test_get_user_info(
        async_client: AsyncClient,
        auth_header_user: dict[str, str],
) -> None:
    response = await async_client.get(
        "/api/v1/auth/user-info",
        headers=auth_header_user,
    )

    assert response.status_code == 200

    json_response = response.json()
    assert json_response["sub"] == PROJECT_SETTINGS.USER_USERNAME
    assert "exp" in json_response
    assert json_response["first_name"] == "Alice"
    assert json_response["last_name"] == "Maxwell"
    assert json_response["is_manager"] is False
