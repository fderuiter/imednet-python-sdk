from unittest.mock import MagicMock

from imednet.models.records import Record
from imednet.workflows.data_extraction import DataExtractionWorkflow


def test_extract_records_by_criteria_omits_none_filter() -> None:
    sdk = MagicMock()
    record = Record.model_validate({"recordId": 1})
    sdk.records.list.return_value = [record]

    wf = DataExtractionWorkflow(sdk)
    result = wf.extract_records_by_criteria("STUDY")

    assert result == [record]
    sdk.records.list.assert_called_once_with("STUDY")
