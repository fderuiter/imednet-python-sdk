"""Unit tests for utils dates and filters."""

from datetime import datetime, timedelta, timezone

import pytest

from imednet.utils.dates import format_iso_datetime, parse_iso_datetime
from imednet.utils.filters import build_filter_string


def test_parse_iso_datetime_with_z() -> None:
    """Test that parse iso datetime with z."""
    dt = parse_iso_datetime("2024-01-01T12:30:00Z")
    assert dt == datetime(2024, 1, 1, 12, 30, 0, tzinfo=timezone.utc)


def test_parse_iso_datetime_with_offset() -> None:
    """Test that parse iso datetime with offset."""
    dt = parse_iso_datetime("2024-01-01T12:30:00+02:00")
    assert dt.hour == 12
    assert dt.tzinfo is not None
    assert dt.tzinfo.utcoffset(dt) == timedelta(hours=2)


def test_parse_iso_datetime_naive() -> None:
    """Test that parse iso datetime naive."""
    dt = parse_iso_datetime("2024-01-01T12:30:00")
    assert dt.tzinfo is None
    assert dt.year == 2024


def test_parse_iso_datetime_millis_padding() -> None:
    """Test that parse iso datetime millis padding."""
    dt = parse_iso_datetime("2021-12-09T08:23:21.99")
    assert dt.microsecond == 990000
    assert dt.tzinfo is None


def test_parse_iso_datetime_micro_padding() -> None:
    """Test that parse iso datetime micro padding."""
    dt = parse_iso_datetime("2025-06-30T21:40:44.98268")
    assert dt.microsecond == 982680


def test_parse_iso_datetime_invalid() -> None:
    """Test that parse iso datetime invalid."""
    with pytest.raises(ValueError):
        parse_iso_datetime("not-a-date")


def test_parse_iso_datetime_none() -> None:
    """Test that parse iso datetime none."""
    with pytest.raises((AttributeError, TypeError)):
        parse_iso_datetime(None)  # type: ignore[arg-type]


def test_format_iso_datetime_aware() -> None:
    """Test that format iso datetime aware."""
    dt = datetime(2024, 1, 1, 12, 30, 0, tzinfo=timezone(timedelta(hours=2)))
    result = format_iso_datetime(dt)
    assert result == "2024-01-01T10:30:00Z"


def test_format_iso_datetime_naive() -> None:
    """Test that format iso datetime naive."""
    dt = datetime(2024, 1, 1, 12, 30, 0)
    result = format_iso_datetime(dt)
    assert result == "2024-01-01T12:30:00Z"


def test_build_filter_string_simple() -> None:
    """Test that build filter string simple."""
    result = build_filter_string({"name": "Alice"})
    assert result == "name==Alice"


def test_build_filter_string_multiple() -> None:
    """Test that build filter string multiple."""
    result = build_filter_string({"name": "A", "age": 30})
    assert result == "name==A;age==30"


def test_build_filter_string_tuple_and_list() -> None:
    """Test that build filter string tuple and list."""
    result = build_filter_string({"age": (">", 20), "type": ["A", "B"]})
    assert result == "age>20;type==A,type==B"


def test_build_filter_string_bool_and_none() -> None:
    """Test that build filter string bool and none."""
    result = build_filter_string({"active": True, "missing": None})
    assert result == "active==True;missing==None"


def test_build_filter_string_empty() -> None:
    """Test that build filter string empty."""
    assert build_filter_string({}) == ""


def test_build_filter_string_snake_to_camel() -> None:
    """Test that build filter string snake to camel."""
    result = build_filter_string({"form_name": "Demo", "visit_date": (">=", "2024")})
    assert result == "formName==Demo;visitDate>=2024"


def test_build_filter_string_snake_list() -> None:
    """Test that build filter string snake list."""
    result = build_filter_string({"field_name": ["A", "B"]})
    assert result == "fieldName==A,fieldName==B"


def test_build_filter_string_quotes() -> None:
    """Test that build filter string quotes."""
    result = build_filter_string({"site_name": "My Site"})
    assert result == 'siteName=="My Site"'


def test_build_filter_string_quote_spaces() -> None:
    """Test that build filter string quote spaces."""
    result = build_filter_string({"site_name": "A B"})
    assert result == 'siteName=="A B"'


def test_build_filter_string_backslashes() -> None:
    """Test that build filter string backslashes."""
    result = build_filter_string({"path": r"C:\Temp", "quote": r"A\"B"})
    # path: C:\Temp -> "C:\\Temp"
    # quote: A\"B -> "A\\\"B"
    assert result == r'path=="C:\\Temp";quote=="A\\\"B"'
