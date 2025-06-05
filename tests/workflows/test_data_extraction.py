from unittest.mock import MagicMock

import pytest

from imednet.core.exceptions import ImednetError
from imednet.workflows.data_extraction import DataExtractionWorkflow


@pytest.fixture
def mock_sdk():
    sdk = MagicMock()
    return sdk


def test_extract_records_no_results(mock_sdk):
    mock_sdk.subjects.list.return_value = []
    mock_sdk.visits.list.return_value = []
    mock_sdk.records.list.return_value = []
    workflow = DataExtractionWorkflow(mock_sdk)

    with pytest.raises(ImednetError):
        workflow.extract_records_by_criteria("STUDY", {})
