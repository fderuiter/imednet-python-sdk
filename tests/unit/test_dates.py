from datetime import datetime, timedelta, timezone

import pytest
from imednet.utils.dates import parse_iso_datetime


def test_parse_iso_datetime_with_z():
    dt = parse_iso_datetime("2023-06-01T12:34:56Z")
    assert dt == datetime(2023, 6, 1, 12, 34, 56, tzinfo=timezone.utc)


def test_parse_iso_datetime_with_utc_offset():
    dt = parse_iso_datetime("2023-06-01T12:34:56+00:00")
    assert dt == datetime(2023, 6, 1, 12, 34, 56, tzinfo=timezone.utc)


def test_parse_iso_datetime_with_non_utc_offset():
    dt = parse_iso_datetime("2023-06-01T14:34:56+02:00")
    assert dt == datetime(2023, 6, 1, 14, 34, 56, tzinfo=timezone(timedelta(hours=2)))


def test_parse_iso_datetime_without_timezone():
    # Should return a naive datetime (no tzinfo)
    dt = parse_iso_datetime("2023-06-01T12:34:56")
    assert dt == datetime(2023, 6, 1, 12, 34, 56)


def test_parse_iso_datetime_invalid_string():
    # Should raise ValueError for invalid string
    with pytest.raises(ValueError):
        parse_iso_datetime("not-a-date")


def test_parse_iso_datetime_date_only():
    # Should return a naive datetime (no tzinfo)
    dt = parse_iso_datetime("2023-06-01")
    assert dt == datetime(2023, 6, 1, 0, 0, 0)
