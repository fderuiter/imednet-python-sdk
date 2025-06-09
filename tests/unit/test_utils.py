from datetime import datetime

from imednet.utils.dates import format_iso_datetime, parse_iso_datetime
from imednet.utils.filters import build_filter_string


class TestFilters:
    def test_build_filter_string_basic(self):
        result = build_filter_string({"name": "John", "age": (">", 20)})
        assert result == "name==John;age>20"

    def test_build_filter_string_list(self):
        result = build_filter_string({"type": ["A", "B"]})
        assert result == "type==A,type==B"


class TestDates:
    def test_parse_iso_datetime_z_suffix(self):
        dt = parse_iso_datetime("2020-01-01T12:00:00Z")
        assert dt.tzinfo
        assert dt.isoformat() == "2020-01-01T12:00:00+00:00"

    def test_format_iso_datetime_naive(self):
        dt = datetime(2020, 1, 1, 12, 0, 0)
        formatted = format_iso_datetime(dt)
        assert formatted == "2020-01-01T12:00:00Z"
