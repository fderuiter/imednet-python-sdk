"""TODO: Add docstring."""

import pytest
import typer

from imednet.cli import parse_filter_args


def test_parse_filter_args_none():
    """TODO: Add docstring."""
    assert parse_filter_args(None) is None


def test_parse_filter_args_types():
    """TODO: Add docstring."""
    result = parse_filter_args(["a=1", "b=true", "c=no", "d=text"])
    assert result == {"a": 1, "b": True, "c": "no", "d": "text"}


def test_parse_filter_args_invalid():
    """TODO: Add docstring."""
    with pytest.raises(SystemExit) as exc_info:
        parse_filter_args(["bad"])
    assert exc_info.value.code == 1


def test_parse_filter_args_invalid_escaped(capfd: pytest.CaptureFixture[str]):
    """TODO: Add docstring."""
    with pytest.raises(SystemExit) as exc_info:
        parse_filter_args(["[red]bad[/red]"])
    assert exc_info.value.code == 1

    captured = capfd.readouterr()
    # Rich renders escaped markup as literal text.
    # If it weren't escaped, Rich (in no-color mode) would strip the tags.
    assert "[red]bad[/red]" in captured.out
