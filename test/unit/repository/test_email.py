import uuid

import pytest
from sqlalchemy.orm import Session

import repository.email as email_repo


async def test_update_nonexisting_system_email_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    monkeypatch.setattr(Session, "get", lambda *args, **kwargs: None)

    with pytest.raises(ValueError):
        email_repo.update_system_email_status(Session(), str(uuid.uuid4()))
