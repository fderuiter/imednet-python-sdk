from unittest.mock import Mock

import pytest
import scripts.post_smoke_record as smoke

from imednet.models.variables import Variable


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


def test_build_record_populates_example_values() -> None:
    sdk = Mock()
    sdk.variables.list.return_value = [
        _var("i", "integer"),
        _var("d", "date"),
        _var("t", "string"),
        _var("i2", "integer"),
    ]

    record = smoke.build_record(sdk, "ST", "F1")

    assert record == {
        "formKey": "F1",
        "data": {
            "i": smoke.EXAMPLE_VALUES["integer"],
            "d": smoke.EXAMPLE_VALUES["date"],
            "t": smoke.EXAMPLE_VALUES["string"],
        },
    }
