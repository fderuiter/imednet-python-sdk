from datetime import datetime, timedelta, timezone

import pytest

from imednet.utils.dates import format_iso_datetime, parse_iso_datetime
from imednet.utils.filters import build_filter_string


def test_parse_iso_datetime_with_z() -> None:
    dt = parse_iso_datetime("2024-01-01T12:30:00Z")
    assert dt == datetime(2024, 1, 1, 12, 30, 0, tzinfo=timezone.utc)


def test_parse_iso_datetime_with_offset() -> None:
    dt = parse_iso_datetime("2024-01-01T12:30:00+02:00")
    assert dt.hour == 12
    assert dt.tzinfo is not None
    assert dt.tzinfo.utcoffset(dt) == timedelta(hours=2)


def test_parse_iso_datetime_naive() -> None:
    dt = parse_iso_datetime("2024-01-01T12:30:00")
    assert dt.tzinfo is None
    assert dt.year == 2024


def test_parse_iso_datetime_invalid() -> None:
    with pytest.raises(ValueError):
        parse_iso_datetime("not-a-date")


def test_parse_iso_datetime_none() -> None:
    with pytest.raises(AttributeError):
        parse_iso_datetime(None)  # type: ignore[arg-type]


def test_format_iso_datetime_aware() -> None:
    dt = datetime(2024, 1, 1, 12, 30, 0, tzinfo=timezone(timedelta(hours=2)))
    result = format_iso_datetime(dt)
    assert result == "2024-01-01T10:30:00Z"


def test_format_iso_datetime_naive() -> None:
    dt = datetime(2024, 1, 1, 12, 30, 0)
    result = format_iso_datetime(dt)
    assert result == "2024-01-01T12:30:00Z"


def test_build_filter_string_simple() -> None:
    result = build_filter_string({"name": "Alice"})
    assert result == "name==Alice"


def test_build_filter_string_multiple() -> None:
    result = build_filter_string({"name": "A", "age": 30})
    assert result == "name==A;age==30"


def test_build_filter_string_tuple_and_list() -> None:
    result = build_filter_string({"age": (">", 20), "type": ["A", "B"]})
    assert result == "age>20;type==A,type==B"


def test_build_filter_string_bool_and_none() -> None:
    result = build_filter_string({"active": True, "missing": None})
    assert result == "active==True;missing==None"


def test_build_filter_string_empty() -> None:
    assert build_filter_string({}) == ""


def test_build_filter_string_snake_to_camel() -> None:
    result = build_filter_string({"form_name": "Demo", "visit_date": (">=", "2024")})
    assert result == "formName==Demo;visitDate>=2024"


def test_build_filter_string_snake_list() -> None:
    result = build_filter_string({"field_name": ["A", "B"]})
    assert result == "fieldName==A,fieldName==B"


def test_build_filter_string_quotes() -> None:
    result = build_filter_string({"site_name": "My Site"})
    assert result == 'siteName=="My Site"'


def test_build_filter_string_quote_spaces() -> None:
    result = build_filter_string({"site_name": "A B"})
    assert result == 'siteName=="A B"'
