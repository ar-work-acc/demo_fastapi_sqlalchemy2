import pytest

from model.common import is_email_valid
from model.employee import Employee


def test_invalid_email():
    assert is_email_valid("invalid_email") is False


def test_employee_invalid_email():
    with pytest.raises(ValueError) as excinfo:
        Employee(
            email="invalid_email",
            first_name="test",
        )
    assert "Email validation failed!" in str(excinfo.value)
