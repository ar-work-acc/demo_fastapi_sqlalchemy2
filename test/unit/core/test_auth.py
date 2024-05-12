from datetime import datetime, timezone

from jose import jwt
from pytest import approx

from core.auth import create_access_token, get_password_hash, verify_password
from core.config import PROJECT_SETTINGS
from model.employee import Employee


def test_get_password_hash():
    # Test a simple password
    password = "mysecretpassword"
    hashed_password = get_password_hash(password)
    assert hashed_password is not None
    assert isinstance(hashed_password, str)

    # Test an empty password
    empty_password = ""
    hashed_empty_password = get_password_hash(empty_password)
    assert hashed_empty_password is not None
    assert isinstance(hashed_empty_password, str)


def test_verify_password():
    # Test correct password
    password = "mysecretpassword"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)

    # Test incorrect password
    wrong_password = "wrongpassword"
    assert not verify_password(wrong_password, hashed_password)

    # Test empty password
    empty_password = ""
    hashed_empty_password = get_password_hash(empty_password)
    assert verify_password(empty_password, hashed_empty_password)


def test_create_access_token_without_expire_time():
    start_datetime = datetime.now(timezone.utc)

    employee = Employee(
        email="stub@email.com",
        first_name="test_fn",
        last_name="test_ln",
        is_manager=False,
    )

    encoded_jwt_token = create_access_token(employee)

    decoded = jwt.decode(
        encoded_jwt_token,
        PROJECT_SETTINGS.JWT_SECRET_KEY,
        PROJECT_SETTINGS.JWT_ALGORITHM,
    )

    token_expire_dt = datetime.fromtimestamp(decoded["exp"], timezone.utc)
    diff = token_expire_dt - start_datetime

    assert diff.total_seconds() == approx(15*60, rel=1e-2)
