import datetime

import pytest

from imednet.utils import validators


def test_parse_bool_various_inputs():
    assert validators.parse_bool(True) is True
    assert validators.parse_bool("yes") is True
    assert validators.parse_bool("0") is False
    assert validators.parse_bool(1) is True
    assert validators.parse_bool("maybe") is False


def test_parse_int_or_default_and_str_default():
    assert validators.parse_int_or_default("5") == 5
    assert validators.parse_int_or_default(None, default=2) == 2
    assert validators.parse_int_or_default("bad") == 0
    with pytest.raises(ValueError):
        validators.parse_int_or_default("bad", strict=True)
    assert validators.parse_str_or_default(None) == ""
    assert validators.parse_str_or_default(123) == "123"


def test_parse_list_and_dict_helpers():
    assert validators.parse_list_or_default(None) == []
    assert validators.parse_list_or_default("a") == ["a"]
    assert validators.parse_list_or_default([1, 2]) == [1, 2]
    assert validators.parse_dict_or_default(None) == {}
    assert validators.parse_dict_or_default({"a": 1}) == {"a": 1}
    with pytest.raises(TypeError):
        validators.parse_dict_or_default("bad")


def test_parse_datetime_wrapper():
    dt = datetime.datetime(2024, 1, 1)
    assert validators.parse_datetime(dt) == dt
    iso = "2024-01-01T00:00:00Z"
    parsed = validators.parse_datetime(iso)
    assert isinstance(parsed, datetime.datetime)
    assert validators.parse_datetime("") == datetime.datetime(1969, 4, 20, 16, 20)


def test_parse_datetime_default_date() -> None:
    """Return a sentinel date when given an empty or ``None`` value."""
    sentinel = datetime.datetime(1969, 4, 20, 16, 20)
    assert validators.parse_datetime("") == sentinel
    assert validators.parse_datetime(None) == sentinel  # type: ignore[arg-type]


def test_parse_datetime_parses_strings() -> None:
    """Parse ISO formatted strings into ``datetime`` objects."""
    iso = "2024-01-01T00:00:00Z"
    parsed = validators.parse_datetime(iso)
    assert parsed == datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
