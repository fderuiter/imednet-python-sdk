import pytest
from imednet.models.validators import parse_bool, parse_int_or_default, parse_str_or_default


class TestValidators:
    def test_parse_bool_various_inputs(self):
        assert parse_bool(True) is True
        assert parse_bool("true") is True
        assert parse_bool("FALSE") is False
        assert parse_bool("random") is False
        assert parse_bool(1) is True

    def test_parse_int_or_default(self):
        assert parse_int_or_default("10") == 10
        assert parse_int_or_default(None, default=5) == 5
        assert parse_int_or_default("bad") == 0
        with pytest.raises(ValueError):
            parse_int_or_default("bad", strict=True)

    def test_parse_str_or_default(self):
        assert parse_str_or_default("abc") == "abc"
        assert parse_str_or_default(None) == ""
