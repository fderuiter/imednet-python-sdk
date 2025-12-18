from unittest.mock import MagicMock

import pytest

from imednet.models.records import Record
from imednet.utils.pandas import export_records_csv


@pytest.fixture
def mock_sdk():
    sdk = MagicMock()
    # Create a record with malicious data
    record_data = {
        "record_id": "1",
        "subject_key": "S1",
        "record_data": {"field": "=cmd|' /C calc'!A0"},
    }
    record = MagicMock(spec=Record)
    # mock model_dump to return the dict
    record.model_dump.return_value = record_data
    sdk.records.list.return_value = [record]
    return sdk


def test_export_records_csv_sanitization(mock_sdk, tmp_path):
    """Verify that CSV export sanitizes formula injection attempts."""
    output_file = tmp_path / "output.csv"

    export_records_csv(mock_sdk, "study_key", str(output_file), flatten=True)

    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check that the malicious value is prefixed with a single quote
    # The output should contain: ..., ' =cmd...
    # Pandas to_csv might quote the field if it contains special chars.
    # If sanitized, it becomes "'=cmd..."
    # If not sanitized, it is "=cmd..."

    # We expect the sanitized version to be present
    assert "'=cmd|' /C calc'!A0" in content
