from datetime import datetime

import pytest
from imednet.models.validators import (
    _or_default,
    parse_bool,
    parse_datetime,
    parse_dict_or_default,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)


def test_or_default():
    assert _or_default(None, "default") == "default"
    assert _or_default("value", "default") == "value"
    assert _or_default(0, 1) == 0


def test_parse_datetime():
    # Test empty value returns default date
    assert parse_datetime("") == datetime(1969, 4, 20, 16, 20)

    # Test datetime object passes through
    dt = datetime(2023, 1, 1)
    assert parse_datetime(dt) == dt

    # Test ISO string parsing (assuming parse_iso_datetime works)
    assert isinstance(parse_datetime("2023-01-01T00:00:00Z"), datetime)


def test_parse_bool():
    # Test boolean values
    assert parse_bool(True) is True
    assert parse_bool(False) is False

    # Test string values
    assert parse_bool("true") is True
    assert parse_bool("1") is True
    assert parse_bool("yes") is True
    assert parse_bool("false") is False
    assert parse_bool("0") is False
    assert parse_bool("no") is False

    # Test numeric values
    assert parse_bool(1) is True
    assert parse_bool(0) is False
    assert parse_bool(1.0) is True
    assert parse_bool(0.0) is False

    # Test invalid values default to False
    assert parse_bool(None) is False
    assert parse_bool("invalid") is False


def test_parse_int_or_default():
    # Test valid integers
    assert parse_int_or_default(5) == 5
    assert parse_int_or_default("5") == 5

    # Test defaults
    assert parse_int_or_default(None) == 0
    assert parse_int_or_default("") == 0
    assert parse_int_or_default(None, default=42) == 42

    # Test strict mode
    with pytest.raises(ValueError):
        parse_int_or_default("invalid", strict=True)
    assert parse_int_or_default("invalid", strict=False) == 0


def test_parse_str_or_default():
    assert parse_str_or_default("test") == "test"
    assert parse_str_or_default(None) == ""
    assert parse_str_or_default(None, default="default") == "default"
    assert parse_str_or_default(123) == "123"


def test_parse_list_or_default():
    # Test None value
    assert parse_list_or_default(None) == []

    # Test list passthrough
    assert parse_list_or_default([1, 2, 3]) == [1, 2, 3]

    # Test single value to list conversion
    assert parse_list_or_default(1) == [1]

    # Test custom default factory
    assert parse_list_or_default(None, default_factory=lambda: [1]) == [1]


def test_parse_dict_or_default():
    # Test None value
    assert parse_dict_or_default(None) == {}

    # Test dict passthrough
    test_dict = {"key": "value"}
    assert parse_dict_or_default(test_dict) == test_dict

    # Test non-dict returns empty dict
    assert parse_dict_or_default("not a dict") == {}

    # Test custom default factory
    assert parse_dict_or_default(None, default_factory=lambda: {"default": True}) == {
        "default": True
    }
