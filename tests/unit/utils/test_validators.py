import datetime

import pytest

from imednet.utils.validators import (
    parse_bool,
    parse_datetime,
    parse_dict_or_default,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        ("true", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("y", True),
        ("t", True),
        ("false", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("n", False),
        ("f", False),
        (1, True),
        (0, False),
        (1.0, True),
        (0.0, False),
        ("1.0", True),
        ("0.0", False),
    ],
)
def test_parse_bool(value, expected):
    """Test that parse_bool correctly parses various values."""
    assert parse_bool(value) == expected


def test_parse_bool_invalid_string_raises_error():
    """Test that parse_bool raises a ValueError for invalid strings."""
    with pytest.raises(ValueError):
        parse_bool("not-a-boolean")
    with pytest.raises(ValueError):
        parse_bool("maybe")


def test_parse_bool_invalid_type_raises_error():
    """Test that parse_bool raises a TypeError for invalid types."""
    with pytest.raises(TypeError):
        parse_bool([])
    with pytest.raises(TypeError):
        parse_bool({})
    with pytest.raises(TypeError):
        parse_bool(None)


def test_parse_int_or_default():
    """Test that parse_int_or_default correctly parses values."""
    assert parse_int_or_default("1") == 1
    assert parse_int_or_default(None, default=5) == 5
    assert parse_int_or_default("", default=5) == 5
    assert parse_int_or_default("invalid", default=5) == 5
    with pytest.raises(ValueError):
        parse_int_or_default("invalid", strict=True)
    assert parse_int_or_default("5") == 5
    assert parse_int_or_default(None, default=2) == 2
    assert parse_int_or_default("bad") == 0
    with pytest.raises(ValueError):
        parse_int_or_default("bad", strict=True)


def test_parse_str_or_default():
    """Test that parse_str_or_default correctly parses values."""
    assert parse_str_or_default("hello") == "hello"
    assert parse_str_or_default(None, default="world") == "world"
    assert parse_str_or_default(123) == "123"
    assert parse_str_or_default(None) == ""


def test_parse_list_or_default():
    """Test that parse_list_or_default correctly parses values."""
    assert parse_list_or_default([1, 2, 3]) == [1, 2, 3]
    assert parse_list_or_default(None) == []
    assert parse_list_or_default(1) == [1]
    assert parse_list_or_default("a") == ["a"]


def test_parse_dict_or_default_with_dict():
    """Test that parse_dict_or_default returns the dict if it's a dict."""
    assert parse_dict_or_default({"a": 1}) == {"a": 1}


def test_parse_dict_or_default_with_none():
    """Test that parse_dict_or_default returns a default dict if it's None."""
    assert parse_dict_or_default(None) == {}


def test_parse_dict_or_default_with_none_and_factory():
    """Test that parse_dict_or_default respects the default_factory."""
    assert parse_dict_or_default(None, default_factory=lambda: {"a": 1}) == {"a": 1}


def test_parse_dict_or_default_with_invalid_type_fails():
    """Test that parse_dict_or_default raises TypeError for invalid types."""
    with pytest.raises(TypeError):
        parse_dict_or_default("not a dict")
    with pytest.raises(TypeError):
        parse_dict_or_default(123)
    with pytest.raises(TypeError):
        parse_dict_or_default([1, 2, 3])
    with pytest.raises(TypeError):
        parse_dict_or_default("bad")


def test_parse_datetime_wrapper():
    dt = datetime.datetime(2024, 1, 1)
    assert parse_datetime(dt) == dt
    iso = "2024-01-01T00:00:00Z"
    parsed = parse_datetime(iso)
    assert isinstance(parsed, datetime.datetime)
    assert parse_datetime("") == datetime.datetime(1969, 4, 20, 16, 20)


def test_parse_datetime_default_date() -> None:
    """Return a sentinel date when given an empty or ``None`` value."""
    sentinel = datetime.datetime(1969, 4, 20, 16, 20)
    assert parse_datetime("") == sentinel
    assert parse_datetime(None) == sentinel


def test_parse_datetime_parses_strings() -> None:
    """Parse ISO formatted strings into ``datetime`` objects."""
    iso = "2024-01-01T00:00:00Z"
    parsed = parse_datetime(iso)
    assert parsed == datetime.datetime(2024, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
