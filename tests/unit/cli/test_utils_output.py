import pytest

from imednet.cli.utils import display_list, echo_fetch


def test_echo_fetch_records(capfd: pytest.CaptureFixture[str]) -> None:
    """echo_fetch prints study-specific fetching message."""
    echo_fetch("records", "ST")
    captured = capfd.readouterr()
    assert captured.out == "Fetching records for study 'ST'...\n"
    assert captured.err == ""


def test_display_list_non_empty(capfd: pytest.CaptureFixture[str]) -> None:
    """display_list shows count and items for non-empty lists."""
    display_list([1, 2], "items")
    captured = capfd.readouterr()
    assert captured.out == "Found 2 items:\n[1, 2]\n"
    assert captured.err == ""


def test_display_list_empty(capfd: pytest.CaptureFixture[str]) -> None:
    """display_list prints default message for empty lists."""
    display_list([], "items")
    captured = capfd.readouterr()
    assert captured.out == "No items found.\n"
    assert captured.err == ""
