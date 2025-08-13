from unittest.mock import Mock

import pytest
import scripts.post_smoke_record as smoke

from imednet.models.variables import Variable
from imednet.testing import typed_values


def test_submit_record_uses_configured_timeout() -> None:
    sdk = Mock()
    sdk.records.create.return_value = Mock(batch_id="B1")
    sdk.poll_job.return_value = Mock(state="COMPLETED", batch_id="B1")

    batch_id = smoke.submit_record(sdk, "ST", {"data": {}}, timeout=123)

    assert batch_id == "B1"
    sdk.poll_job.assert_called_once_with("ST", "B1", interval=1, timeout=123)


def test_submit_record_reports_failure_details() -> None:
    sdk = Mock()
    sdk.records.create.return_value = Mock(batch_id="B1")
    sdk.poll_job.return_value = Mock(state="FAILED", batch_id="B1", result_url="https://x")
    response = Mock(text="Form with formKey of SS not found.")
    response.json.side_effect = ValueError()
    sdk._client.get.return_value = response

    with pytest.raises(RuntimeError, match="FAILED: Form with formKey"):
        smoke.submit_record(sdk, "ST", {"data": {}}, timeout=1)

    sdk._client.get.assert_called_once_with("https://x")


def _var(name: str, var_type: str) -> Variable:
    return Variable(variable_name=name, variable_type=var_type, form_id=1, form_key="F1")


def test_build_record_populates_typed_values() -> None:
    sdk = Mock()
    sdk.variables.list.return_value = [
        _var("text", "text"),
        _var("date", "date"),
        _var("num", "integer"),
        _var("rad", "radio"),
        _var("drop", "dropdown"),
        _var("memo", "memo"),
        _var("check", "checkbox"),
        _var("extra", "text"),
    ]

    record = smoke.build_record(
        sdk, "ST", "F1", site_name="S", subject_key="SUB", interval_name="INT"
    )

    expected = {
        "text": typed_values.value_for("text"),
        "date": typed_values.value_for("date"),
        "num": typed_values.value_for("integer"),
        "rad": typed_values.value_for("radio"),
        "drop": typed_values.value_for("dropdown"),
        "memo": typed_values.value_for("memo"),
        "check": typed_values.value_for("checkbox"),
    }
    assert record == {
        "formKey": "F1",
        "data": expected,
        "siteName": "S",
        "subjectKey": "SUB",
        "intervalName": "INT",
    }
    sdk.variables.list.assert_called_once_with(study_key="ST", formKey="F1")
