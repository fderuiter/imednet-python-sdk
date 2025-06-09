import types
from typing import List
from unittest.mock import MagicMock

from imednet.models.records import Record
from imednet.workflows.data_quality import DataQualityWorkflow


def make_variable(name: str, required: bool = False):
    return types.SimpleNamespace(variable_name=name, required=required, disabled=False)


def make_record(record_id: int, data: dict) -> Record:
    return Record(record_id=record_id, record_data=data)


def make_coding(record_id: int, variable: str, value: str):
    return types.SimpleNamespace(record_id=record_id, variable=variable, value=value)


def setup_sdk(variables: List, records: List[Record], codings: List):
    sdk = MagicMock()
    sdk.variables.list.return_value = variables
    sdk.records.list.return_value = records
    sdk.codings.list.return_value = codings
    return sdk


def test_check_missing_required_calls_endpoints() -> None:
    vars_ = [make_variable("a", required=True), make_variable("b", required=False)]
    recs = [make_record(1, {"a": "", "b": 1}), make_record(2, {"a": "1", "b": 2})]
    sdk = setup_sdk(vars_, recs, [])

    workflow = DataQualityWorkflow(sdk)
    result = workflow.check_missing_required("STUDY")

    sdk.variables.list.assert_called_with("STUDY")
    sdk.records.list.assert_called_with("STUDY")
    assert result == [recs[0]]


def test_check_coding_consistency_detects_mismatch() -> None:
    vars_ = []
    recs = [make_record(1, {"a": "x"})]
    codings = [make_coding(1, "a", "y")]
    sdk = setup_sdk(vars_, recs, codings)

    workflow = DataQualityWorkflow(sdk)
    result = workflow.check_coding_consistency("STUDY")

    sdk.codings.list.assert_called_with("STUDY")
    sdk.records.list.assert_called_with("STUDY")
    assert len(result) == 1
    assert result[0][0] is recs[0]
    assert "does not match" in result[0][1]
