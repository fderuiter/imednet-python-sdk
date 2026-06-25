"""Tests for test_parse_filters."""

import pytest
import typer

from imednet.cli import parse_filter_args


def test_parse_filter_args_none():
    """Test test_parse_filter_args_none behavior."""
    assert parse_filter_args(None) is None


def test_parse_filter_args_types():
    """Test test_parse_filter_args_types behavior."""
    result = parse_filter_args(["a=1", "b=true", "c=no", "d=text"])
    assert result == {"a": 1, "b": True, "c": "no", "d": "text"}


def test_parse_filter_args_invalid():
    """Test test_parse_filter_args_invalid behavior."""
    with pytest.raises(typer.Exit) as exc_info:
        parse_filter_args(["bad"])
    assert exc_info.value.exit_code == 1


def test_parse_filter_args_invalid_escaped(capfd: pytest.CaptureFixture[str]):
    """Test test_parse_filter_args_invalid_escaped behavior."""
    with pytest.raises(typer.Exit) as exc_info:
        parse_filter_args(["[red]bad[/red]"])
    assert exc_info.value.exit_code == 1

    captured = capfd.readouterr()
    # Rich renders escaped markup as literal text.
    # If it weren't escaped, Rich (in no-color mode) would strip the tags.
    assert "[red]bad[/red]" in captured.out
