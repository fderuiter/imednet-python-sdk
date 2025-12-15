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


def test_parse_filter_args_invalid_escaped(capfd: pytest.CaptureFixture[str]):
    with pytest.raises(Exception):
        parse_filter_args(["[red]bad[/red]"])

    captured = capfd.readouterr()
    # Rich renders escaped markup as literal text.
    # If it weren't escaped, Rich (in no-color mode) would strip the tags.
    assert "[red]bad[/red]" in captured.out
