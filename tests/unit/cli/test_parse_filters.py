import pytest
from imednet.cli import parse_filter_args


def test_parse_filter_args_none():
    assert parse_filter_args(None) is None


def test_parse_filter_args_types():
    result = parse_filter_args(["a=1", "b=true", "c=no", "d=text"])
    assert result == {"a": 1, "b": True, "c": "no", "d": "text"}


def test_parse_filter_args_invalid():
    with pytest.raises(Exception):
        parse_filter_args(["bad"])
