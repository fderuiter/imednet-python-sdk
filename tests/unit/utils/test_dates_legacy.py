from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from imednet.utils import dates


@pytest.mark.unit
def test_parse_iso_datetime_legacy_high_precision():
    """
    Ensure that on Python < 3.11, high precision fractional seconds are truncated.
    Simulates legacy environment where >6 digit precision raises ValueError.
    """

    # Define a side_effect that simulates Python 3.10 limitation
    def picky_fromisoformat(date_str):
        import re

        # Find fractional seconds
        match = re.search(r"\.(\d+)", date_str)
        if match:
            frac = match.group(1)
            if len(frac) > 6:
                msg = f"Invalid isoformat string: '{date_str}' (simulated legacy limitation)"
                raise ValueError(msg)

        # In a real scenario we'd call the real datetime.fromisoformat,
        # but here we just return a dummy to prove success
        return datetime(2025, 6, 30, 21, 40, 44, 123456, tzinfo=timezone.utc)

    # Force the module to use the legacy path
    with patch.object(dates, "_IS_PY311_OR_GREATER", False):
        # Patch the datetime class imported in the module
        with patch("imednet.utils.dates.datetime") as mock_dt:
            mock_dt.fromisoformat.side_effect = picky_fromisoformat
            mock_dt.timezone = timezone

            # Act
            result = dates.parse_iso_datetime("2025-06-30T21:40:44.1234567")

            # Assert
            assert result.microsecond == 123456

            # Verify that fromisoformat was called with a truncated string
            call_args = mock_dt.fromisoformat.call_args
            assert call_args is not None
            called_str = call_args[0][0]

            # It should have exactly 6 digits of precision
            assert ".123456" in called_str
            assert ".1234567" not in called_str
