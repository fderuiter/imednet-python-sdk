import datetime

import pytest

from imednet.utils import validators


@pytest.mark.parametrize(
    "input_val, expected",
    [
        # Boolean inputs
        (True, True),
        (False, False),
        # String inputs - True variants (optimized)
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("y", True),
        ("t", True),
        # String inputs - False variants (optimized)
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("n", False),
        ("f", False),
        # String inputs - Whitespace/Case (fallback path)
        (" true ", True),
        (" Yes ", True),
        ("TrUe", True),
        (" FALSE ", False),
        (" No ", False),
        ("FaLsE", False),
        # Numeric inputs
        (1, True),
        (0, False),
        (1.0, True),
        (0.0, False),
        (-1, True),  # Non-zero number is True
        # Edge cases / Invalid
        (None, False),
        ("maybe", False),
        ("", False),
        ([], False),
        ({}, False),
    ],
)
def test_parse_bool_comprehensive(input_val, expected):
    assert validators.parse_bool(input_val) is expected


def test_parse_int_or_default_and_str_default():
    assert validators.parse_int_or_default("5") == 5
    assert validators.parse_int_or_default(None, default=2) == 2
    assert validators.parse_int_or_default("bad") == 0
    with pytest.raises(ValueError):
        validators.parse_int_or_default("bad", strict=True)

    # Float string robustness
    assert validators.parse_int_or_default("5.0") == 5
    assert validators.parse_int_or_default("5.9") == 5
    assert validators.parse_int_or_default(5.9) == 5
    assert validators.parse_int_or_default("inf") == 0
    with pytest.raises(OverflowError):
        validators.parse_int_or_default("inf", strict=True)

    assert validators.parse_str_or_default(None) == ""
    assert validators.parse_str_or_default(123) == "123"


def test_parse_list_and_dict_helpers():
    assert validators.parse_list_or_default(None) == []
    assert validators.parse_list_or_default("a") == ["a"]
    assert validators.parse_list_or_default([1, 2]) == [1, 2]
    assert validators.parse_dict_or_default(None) == {}
    assert validators.parse_dict_or_default({"a": 1}) == {"a": 1}
    assert validators.parse_dict_or_default("bad") == {}


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
