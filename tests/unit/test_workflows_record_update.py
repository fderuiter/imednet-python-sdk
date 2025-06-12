from unittest.mock import MagicMock

import pytest
from imednet.core.exceptions import ValidationError
from imednet.models.jobs import Job
from imednet.models.variables import Variable
from imednet.utils.schema import SchemaCache
from imednet.workflows.record_update import RecordUpdateWorkflow


def test_submit_record_batch_no_wait() -> None:
    sdk = MagicMock()
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.create.return_value = job

    wf = RecordUpdateWorkflow(sdk)
    result = wf.submit_record_batch("STUDY", [{"a": 1}])

    sdk.records.create.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    assert result == job


def test_submit_record_batch_wait_for_completion(monkeypatch) -> None:
    sdk = MagicMock()
    initial_job = Job(batch_id="1", state="PROCESSING")
    completed_job = Job(batch_id="1", state="COMPLETED")
    sdk.records.create.return_value = initial_job
    sdk.jobs.get.side_effect = [initial_job, completed_job]

    wf = RecordUpdateWorkflow(sdk)
    # patch sleep to avoid delay
    monkeypatch.setattr("time.sleep", lambda *args: None)
    result = wf.submit_record_batch(
        "STUDY",
        [{"a": 1}],
        wait_for_completion=True,
        poll_interval=0,
        timeout=5,
    )

    sdk.records.create.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    sdk.jobs.get.assert_called_with("STUDY", "1")
    assert result.state == "COMPLETED"


def test_update_scheduled_record_builds_payload() -> None:
    sdk = MagicMock()
    wf = RecordUpdateWorkflow(sdk)
    wf.submit_record_batch = MagicMock(return_value="job")

    result = wf.update_scheduled_record(
        "STUDY",
        form_identifier="F1",
        subject_identifier="SUBJ1",
        interval_identifier="INT1",
        data={"x": 1},
        subject_identifier_type="oid",
    )

    wf.submit_record_batch.assert_called_once()
    called = wf.submit_record_batch.call_args.kwargs
    assert called["records_data"] == [
        {
            "formKey": "F1",
            "subjectOid": "SUBJ1",
            "intervalName": "INT1",
            "data": {"x": 1},
        }
    ]
    assert result == "job"


def test_submit_record_batch_validation() -> None:
    sdk = MagicMock()
    wf = RecordUpdateWorkflow(sdk)

    schema = SchemaCache()
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    schema._form_variables = {"F1": {"age": var}}
    schema._form_id_to_key = {1: "F1"}
    wf._schema = schema

    with pytest.raises(ValidationError):
        wf.submit_record_batch("STUDY", [{"formKey": "F1", "data": {"bad": 1}}])
    sdk.records.create.assert_not_called()

    wf.submit_record_batch("STUDY", [{"formKey": "F1", "data": {"age": 5}}])
    sdk.records.create.assert_called_once()
