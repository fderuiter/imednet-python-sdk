from unittest.mock import MagicMock

import pytest

from imednet.api.core.exceptions import ValidationError
from imednet.api.models.jobs import Job
from imednet.api.models.variables import Variable
from imednet.workflows.record_update import RecordUpdateWorkflow


def test_create_or_update_records_no_wait() -> None:
    sdk = MagicMock()
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.create.return_value = job

    wf = RecordUpdateWorkflow(sdk)
    result = wf.create_or_update_records("STUDY", [{"a": 1}])

    sdk.records.create.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    assert result == job


def test_create_or_update_records_wait_for_completion(monkeypatch) -> None:
    sdk = MagicMock()
    initial_job = Job(batch_id="1", state="PROCESSING")
    completed_job = Job(batch_id="1", state="COMPLETED")
    sdk.records.create.return_value = initial_job
    sdk.jobs.get.side_effect = [initial_job, completed_job]

    wf = RecordUpdateWorkflow(sdk)
    # patch sleep to avoid delay
    monkeypatch.setattr("time.sleep", lambda *args: None)
    result = wf.create_or_update_records(
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
    wf.create_or_update_records = MagicMock(return_value="job")  # type: ignore[method-assign]

    result = wf.update_scheduled_record(
        "STUDY",
        form_identifier="F1",
        subject_identifier="SUBJ1",
        interval_identifier="INT1",
        data={"x": 1},
        subject_identifier_type="oid",
    )

    wf.create_or_update_records.assert_called_once()
    called = wf.create_or_update_records.call_args.kwargs
    assert called["records_data"] == [
        {
            "formKey": "F1",
            "subjectOid": "SUBJ1",
            "intervalName": "INT1",
            "data": {"x": 1},
        }
    ]
    assert result == "job"


def test_create_or_update_records_validation() -> None:
    sdk = MagicMock()
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk.variables.list.return_value = [var]
    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValidationError):
        wf.create_or_update_records("STUDY", [{"formKey": "F1", "data": {"bad": 1}}])
    sdk.records.create.assert_not_called()

    sdk.records.create.return_value = Job(batch_id="1", state="PROCESSING")
    wf.create_or_update_records("STUDY", [{"formKey": "F1", "data": {"age": 5}}])
    sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)
    sdk.records.create.assert_called_once_with(
        "STUDY", [{"formKey": "F1", "data": {"age": 5}}], schema=wf._schema
    )
