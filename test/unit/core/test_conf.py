import pytest
from core.config import parse_cors


def test_parse_cors_string() -> None:
    assert ["a", "b", "c"] == parse_cors("a,b ,  c")


def test_parse_cors_list() -> None:
    three = list()
    three.append("a")
    three.append("b")
    assert three == parse_cors(three)


def test_parse_cors_error() -> None:
    with pytest.raises(ValueError):
        parse_cors(1)
