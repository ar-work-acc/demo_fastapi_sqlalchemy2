import logging
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from core.config import PROJECT_SETTINGS
from main import app

BASE_URL = "http://test"

logger = logging.getLogger(__name__)


# def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
#     """
#     If you want to modify the order of the tests, you can do it here.
#     """
#     for idx, item in enumerate(items):
#         name = item.name
#         if name.endswith("_login"):
#             removed_element = items.pop(idx)
#             items.insert(0, removed_element)

#     logger.debug(" # Loading tests in this order: (login tests run first)")
#     for item in items:
#         logger.debug(item.name)


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """
    For those that don't need a asynchronous client.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app,
        base_url=BASE_URL,
    ) as async_client:
        yield async_client


async def get_auth_header(
    async_client: AsyncClient,
    username: str,
    password: str,
) -> dict[str, str]:
    form_data = {
        "username": username,
        "password": password,
    }
    response = await async_client.post("/api/v1/auth/login", data=form_data)
    token = response.json()["access_token"]
    header = {"Authorization": f"Bearer {token}"}
    return header


@pytest.fixture
async def auth_header_admin(async_client: AsyncClient) -> dict[str, str]:
    header = await get_auth_header(
        async_client,
        PROJECT_SETTINGS.ADMIN_USERNAME,
        PROJECT_SETTINGS.ADMIN_PASSWORD,
    )
    return header


@pytest.fixture
async def auth_header_user(async_client: AsyncClient) -> dict[str, str]:
    header = await get_auth_header(
        async_client,
        PROJECT_SETTINGS.USER_USERNAME,
        PROJECT_SETTINGS.USER_PASSWORD,
    )
    return header
