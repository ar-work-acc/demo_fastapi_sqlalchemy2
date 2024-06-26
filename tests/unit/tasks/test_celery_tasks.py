import uuid
from unittest.mock import MagicMock

import pytest
from celery import Task
from celery.exceptions import Retry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.email import NotificationType, SystemEmail
from task_queue.tasks import send_email

DUMMY_PRODUCT_ID = 999_999


async def test_send_mail(
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    product_id = DUMMY_PRODUCT_ID

    celery_task_id = uuid.uuid4()
    monkeypatch.setattr(
        Task, "request", type("Request", (object,), {"id": celery_task_id})
    )

    # run the celery task directly with mocks
    assert celery_task_id == send_email(product_id)

    stmt = select(SystemEmail).filter_by(task_id=celery_task_id)
    system_email = (await session.scalars(stmt)).one()
    assert system_email.target_id == product_id
    assert system_email.type == NotificationType.PRODUCT
    assert system_email.is_sent


async def test_send_email_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # emulate Task.retry()
    monkeypatch.setattr(Task, "retry", MagicMock(side_effect=Retry))

    # we need to mock SessionMaker
    monkeypatch.setattr(
        "task_queue.tasks.SessionMaker",
        MagicMock(),
    )
    # since we're raising an error when sending an email
    monkeypatch.setattr(
        "task_queue.tasks.create_and_send_system_email",
        MagicMock(side_effect=RuntimeError("Error sending system email!")),
    )

    with pytest.raises(Retry):
        await send_email(DUMMY_PRODUCT_ID)
