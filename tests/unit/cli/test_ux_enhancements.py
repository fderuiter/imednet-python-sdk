from unittest.mock import patch

from imednet.cli.utils import display_list


def test_display_list_ux_enhancements():
    """Verify table has alternating row styles and numeric columns are right-aligned."""
    data = [{"name": "Alice", "age": 30, "score": 95.5, "active": True}]

    with patch("imednet.cli.utils.Table") as mock_table:
        mock_table_instance = mock_table.return_value

        display_list(data, "people")

        # Check Table initialization for row_styles
        mock_table.assert_called_once()
        _, kwargs = mock_table.call_args
        assert kwargs.get("row_styles") == ["none", "dim"]

        # Check add_column calls for justification
        # Expected: Name (left), Age (right), Score (right), Active (left)
        # Note: headers are title-cased
        calls = mock_table_instance.add_column.call_args_list

        # Name
        assert calls[0].args[0] == "Name"
        assert calls[0].kwargs.get("justify", "left") == "left"

        # Age
        assert calls[1].args[0] == "Age"
        assert calls[1].kwargs.get("justify") == "right"

        # Score
        assert calls[2].args[0] == "Score"
        assert calls[2].kwargs.get("justify") == "right"

        # Active
        assert calls[3].args[0] == "Active"
        assert calls[3].kwargs.get("justify", "left") == "left"
