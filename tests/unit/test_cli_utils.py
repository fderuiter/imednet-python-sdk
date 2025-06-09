import pytest
import typer
from imednet.cli import parse_filter_args


def test_parse_filter_args_returns_dict():
    result = parse_filter_args(["age=30", "active=true"])
    assert result == {"age": 30, "active": True}


def test_parse_filter_args_invalid_format():
    with pytest.raises(typer.Exit):
        parse_filter_args(["badformat"])
