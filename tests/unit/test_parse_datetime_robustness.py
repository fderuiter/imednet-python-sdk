from datetime import datetime, timezone

from imednet.utils.validators import parse_datetime


def test_parse_datetime_int_timestamp():
    """Test that parse_datetime correctly handles integer timestamps (seconds)."""
    ts = 1609459200  # 2021-01-01 00:00:00 UTC
    result = parse_datetime(ts)
    assert isinstance(result, datetime)
    assert result == datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def test_parse_datetime_float_timestamp():
    """Test that parse_datetime correctly handles float timestamps (seconds)."""
    ts = 1609459200.5  # 2021-01-01 00:00:00.5 UTC
    result = parse_datetime(ts)
    assert isinstance(result, datetime)
    assert result == datetime(2021, 1, 1, 0, 0, 0, 500000, tzinfo=timezone.utc)


def test_parse_datetime_negative_timestamp():
    """Test that parse_datetime correctly handles negative timestamps (historic dates)."""
    ts = -2208988800  # 1900-01-01 00:00:00 UTC
    result = parse_datetime(ts)
    assert isinstance(result, datetime)
    # Note: Depending on platform/implementation, negative timestamps might behave differently,
    # but Python's fromtimestamp usually handles them on modern systems.
    # We'll check it works generally.
    assert result.year == 1900
    assert result.month == 1
    assert result.day == 1
    assert result.tzinfo == timezone.utc


def test_parse_datetime_zero_timestamp():
    """Test that parse_datetime treats 0 (epoch) as empty/sentinel due to legacy falsy check."""
    ts = 0
    result = parse_datetime(ts)
    # Current behavior: 0 is falsy -> Sentinel.
    # This documents existing behavior rather than enforcing a change.
    assert result == datetime(1969, 4, 20, 16, 20)
