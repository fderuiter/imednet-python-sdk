from unittest.mock import MagicMock

from imednet.models.records import Record
from imednet.workflows.data_quality import DataQualityWorkflow


def test_check_missing_required() -> None:
    sdk = MagicMock()
    sdk.variables.list.return_value = [
        MagicMock(variable_name="age", required=True),
        MagicMock(variable_name="weight", required=False),
    ]
    sdk.records.list.return_value = [
        Record(record_data={"age": 10}),
        Record(record_data={"weight": 70}),
    ]

    wf = DataQualityWorkflow(sdk)
    missing = wf.check_missing_required("S1")

    sdk.variables.list.assert_called_once_with("S1")
    sdk.records.list.assert_called_once_with("S1")
    assert missing == [sdk.records.list.return_value[1]]


def test_check_coding_consistency() -> None:
    sdk = MagicMock()
    sdk.codings.list.return_value = [
        MagicMock(variable="age", value="10"),
        MagicMock(variable="age", value="11"),
    ]
    sdk.records.list.return_value = [
        Record(record_data={"age": 12}),
        Record(record_data={"age": 11}),
    ]

    wf = DataQualityWorkflow(sdk)
    mismatches = wf.check_coding_consistency("S2")

    sdk.codings.list.assert_called_once_with("S2")
    sdk.records.list.assert_called_once_with("S2")
    assert mismatches == [(sdk.records.list.return_value[0], "age: 12 not coded")]
