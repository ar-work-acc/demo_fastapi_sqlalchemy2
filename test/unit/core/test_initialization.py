import logging
from datetime import date, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import PROJECT_SETTINGS
from core.initialize_data import check_and_create_user


async def test_creating_duplicate_user(
    session: AsyncSession,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.DEBUG)

    await check_and_create_user(
        session,
        first_name="Louis",
        last_name="Huang",
        email=PROJECT_SETTINGS.ADMIN_USERNAME,
        password=PROJECT_SETTINGS.ADMIN_PASSWORD,
        is_manager=True,
        hire_date=date.today() - timedelta(days=30),
    )

    for record in caplog.records:
        assert record.levelname != "CRITICAL"

    assert (
        f"User ({PROJECT_SETTINGS.ADMIN_USERNAME})"
        " already exists! Skipping."
    ) in caplog.text
