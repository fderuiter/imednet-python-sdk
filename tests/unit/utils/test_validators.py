"""Test Validators module."""

from datetime import datetime, timezone

import pytest

from imednet.utils.validators import (
    parse_bool,
    parse_datetime,
    parse_dict_or_default,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)


def test_parse_datetime_handles_empty_values():
    """Test the test parse datetime handles empty values functionality."""
    sentinel = datetime(1969, 4, 20, 16, 20)
    assert parse_datetime("") == sentinel
    assert parse_datetime(None) == sentinel


def test_parse_datetime_handles_numeric_timestamps():
    """Test the test parse datetime handles numeric timestamps functionality."""
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    ts = dt.timestamp()
    assert parse_datetime(ts) == dt
    assert parse_datetime(int(ts)) == dt


def test_parse_datetime_handles_zero_timestamps():
    """Test the test parse datetime handles zero timestamps functionality."""
    dt = datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc)
    assert parse_datetime(0) == dt
    assert parse_datetime(0.0) == dt


def test_parse_bool_handles_various_representations():
    """Test the test parse bool handles various representations functionality."""
    assert parse_bool(True) is True
    assert parse_bool("true") is True
    assert parse_bool("1") is True
    assert parse_bool(1) is True
    assert parse_bool("yes") is True
    assert parse_bool("y") is True
    assert parse_bool("t") is True

    assert parse_bool(False) is False
    assert parse_bool("false") is False
    assert parse_bool("0") is False
    assert parse_bool(0) is False
    assert parse_bool("no") is False
    assert parse_bool("n") is False
    assert parse_bool("f") is False


def test_parse_bool_handles_floats():
    """Test the test parse bool handles floats functionality."""
    assert parse_bool("1.0") is True
    assert parse_bool(1.0) is True
    assert parse_bool("0.0") is False
    assert parse_bool(0.0) is False


def test_parse_bool_handles_irregular_casing():
    """Test the test parse bool handles irregular casing functionality."""
    assert parse_bool(" TrUe ") is True
    assert parse_bool(" fAlSe ") is False


def test_parse_bool_returns_false_for_invalid_strings():
    """Test the test parse bool returns false for invalid strings functionality."""
    assert parse_bool("invalid") is False
    assert parse_bool("apple") is False
    assert parse_bool("") is False


def test_parse_int_or_default_handles_valid_ints():
    """Test the test parse int or default handles valid ints functionality."""
    assert parse_int_or_default(42) == 42
    assert parse_int_or_default("42") == 42


def test_parse_int_or_default_handles_floats():
    """Test the test parse int or default handles floats functionality."""
    assert parse_int_or_default(42.0) == 42
    assert parse_int_or_default("42.0") == 42


def test_parse_int_or_default_uses_default_for_empty():
    """Test the test parse int or default uses default for empty functionality."""
    assert parse_int_or_default(None, default=10) == 10
    assert parse_int_or_default("", default=10) == 10


def test_parse_int_or_default_strict_raises_on_invalid():
    """Test the test parse int or default strict raises on invalid functionality."""
    with pytest.raises(ValueError):
        parse_int_or_default("invalid", strict=True)


def test_parse_int_or_default_returns_default_on_invalid_when_not_strict():
    """Test the test parse int or default returns default on invalid when not strict functionality."""
    assert parse_int_or_default("invalid", default=10) == 10


def test_parse_str_or_default():
    """Test the test parse str or default functionality."""
    assert parse_str_or_default("hello") == "hello"
    assert parse_str_or_default(42) == "42"
    assert parse_str_or_default(None, default="default") == "default"


def test_parse_list_or_default():
    """Test the test parse list or default functionality."""
    assert parse_list_or_default([1, 2]) == [1, 2]
    assert parse_list_or_default(42) == [42]
    assert parse_list_or_default(None) == []


def test_parse_dict_or_default():
    """Test the test parse dict or default functionality."""
    assert parse_dict_or_default({"a": 1}) == {"a": 1}
    assert parse_dict_or_default(None) == {}
    assert parse_dict_or_default("invalid") == {}


def test_parse_datetime_handles_datetime_objects():
    """Test the test parse datetime handles datetime objects functionality."""
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert parse_datetime(dt) == dt


def test_parse_datetime_handles_string_timestamps():
    """Test the test parse datetime handles string timestamps functionality."""
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert parse_datetime("2024-01-01T12:00:00Z") == dt


def test_parse_bool_handles_unusual_strings():
    """Test the test parse bool handles unusual strings functionality."""
    # Test cases that trigger the float fallback
    assert parse_bool("inf") is True
    assert parse_bool("nan") is True
    assert parse_bool("1.5") is True
    assert parse_bool("100") is True
    assert parse_bool("-1") is True
    # Test edge cases for float fallback that should return False
    assert parse_bool(".") is False
    assert parse_bool("+") is False
    assert parse_bool("-") is False
    assert parse_bool("n") is False  # 'n' is in _FALSE_LOWER, explicitly False
    assert parse_bool("i") is False  # 'i' not in TRUE/FALSE sets, but triggers float fallback check


def test_parse_bool_handles_non_string_types():
    """Test the test parse bool handles non string types functionality."""
    # Non-truthy values according to rationale should return False
    assert parse_bool(None) is False
    assert parse_bool([]) is False
    assert parse_bool({}) is False
    assert parse_bool(object()) is False


def test_parse_bool_handles_extra_numeric_values():
    """Test the test parse bool handles extra numeric values functionality."""
    # Numeric types are truthy if non-zero
    assert parse_bool(float("inf")) is True
    assert parse_bool(float("nan")) is True
    assert parse_bool(100) is True
    assert parse_bool(-1) is True
