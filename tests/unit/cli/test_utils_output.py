from unittest.mock import MagicMock

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


def test_display_list_table(capfd: pytest.CaptureFixture[str]) -> None:
    """display_list prints a table for objects with model_dump."""
    obj = MagicMock()
    obj.model_dump.return_value = {"my_key": "my_val"}

    display_list([obj], "items")
    captured = capfd.readouterr()

    assert "Found 1 items:" in captured.out
    assert "My Key" in captured.out  # Header title-ized and underscores replaced
    assert "my_val" in captured.out
