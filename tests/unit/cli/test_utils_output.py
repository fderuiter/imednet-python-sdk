from unittest.mock import MagicMock, patch

import pytest

from imednet.cli.utils import _format_cell_value, display_list, fetching_status


def test_fetching_status_records() -> None:
    """fetching_status shows status spinner with message."""
    with patch("imednet.cli.utils.console") as mock_console:
        mock_status = mock_console.status.return_value
        mock_status.__enter__.return_value = None

        with fetching_status("records", "ST"):
            pass

        mock_console.status.assert_called_with(
            "[bold blue]Fetching records for study 'ST'...[/bold blue]", spinner="dots"
        )
        mock_status.__enter__.assert_called()
        mock_status.__exit__.assert_called()


def test_fetching_status_escapes_injection() -> None:
    """fetching_status escapes Rich markup in study key."""
    with patch("imednet.cli.utils.console") as mock_console:
        mock_status = mock_console.status.return_value
        mock_status.__enter__.return_value = None

        with fetching_status("records", "[bold]bad[/bold]"):
            pass

        args, kwargs = mock_console.status.call_args
        msg = args[0]
        # rich.markup.escape escapes brackets
        assert "\\[bold]bad\\[/bold]" in msg


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


def test_display_list_formatting(capfd: pytest.CaptureFixture[str]) -> None:
    """display_list formats booleans and datetimes."""
    from datetime import datetime

    obj = MagicMock()
    obj.model_dump.return_value = {
        "active": True,
        "inactive": False,
        "date": datetime(2023, 1, 1, 12, 0, 0),
        "none": None,
    }
    display_list([obj], "items")
    captured = capfd.readouterr()

    assert "2023-01-01 12:00" in captured.out
    assert "Yes" in captured.out
    assert "No" in captured.out
    assert "-" in captured.out


def test_display_list_formatting_lists(capfd: pytest.CaptureFixture[str]) -> None:
    """display_list formats lists of primitives as comma-separated strings."""
    obj = MagicMock()
    obj.model_dump.return_value = {
        "tags": ["a", "b", "c"],
        "numbers": [1, 2],
        "empty": [],
        "complex": [{"a": 1}],
    }
    display_list([obj], "items")
    captured = capfd.readouterr()

    assert "a, b, c" in captured.out
    assert "1, 2" in captured.out
    assert "-" in captured.out
    # Complex lists fall back to truncation/repr
    assert "[{'a': 1}]" in captured.out


def test_display_list_escaping(capfd: pytest.CaptureFixture[str]) -> None:
    """display_list escapes Rich markup in user data."""
    obj = MagicMock()
    obj.model_dump.return_value = {"content": "[bold red]hack[/bold red]"}

    display_list([obj], "items")
    captured = capfd.readouterr()

    # If escaped, the markup tags are preserved in the output text
    assert "[bold red]hack[/bold red]" in captured.out


def test_display_list_with_fields(capfd: pytest.CaptureFixture[str]) -> None:
    """display_list uses optimized path when fields are provided."""
    obj = MagicMock()
    # Mock attribute access for optimized path
    obj.id = 123
    obj.name = "Test Item"
    # Ensure model_dump is NOT called
    obj.model_dump = MagicMock()

    display_list([obj], "items", fields=["id", "name"])
    captured = capfd.readouterr()

    assert "Found 1 items:" in captured.out
    assert "Id" in captured.out
    assert "Name" in captured.out
    assert "123" in captured.out
    assert "Test Item" in captured.out

    # Verify optimization: model_dump should not be called
    obj.model_dump.assert_not_called()


def test_format_cell_value_status_colors() -> None:
    """Test that status columns are correctly colorized."""
    # Green statuses
    assert _format_cell_value("Active", key="status") == "[green]Active[/green]"
    assert _format_cell_value("Success", key="state") == "[green]Success[/green]"
    assert _format_cell_value("OK", key="status") == "[green]OK[/green]"

    # Yellow statuses
    assert _format_cell_value("Pending", key="status") == "[yellow]Pending[/yellow]"
    assert _format_cell_value("Processing", key="state") == "[yellow]Processing[/yellow]"

    # Red statuses
    assert _format_cell_value("Inactive", key="status") == "[red]Inactive[/red]"
    assert _format_cell_value("Error", key="state") == "[red]Error[/red]"
    assert _format_cell_value("Failed", key="status") == "[red]Failed[/red]"


def test_format_cell_value_non_status_columns() -> None:
    """Test that non-status columns are not colorized based on value."""
    # Even if value matches a status keyword, if key is not status/state, no color
    assert _format_cell_value("Active", key="name") == "Active"
    assert _format_cell_value("Pending", key="description") == "Pending"


def test_format_cell_value_unknown_status() -> None:
    """Test that unknown statuses are not colorized."""
    assert _format_cell_value("UnknownStatus", key="status") == "UnknownStatus"
