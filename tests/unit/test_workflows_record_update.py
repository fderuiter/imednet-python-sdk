from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.errors import ValidationError
from imednet.models.jobs import Job
from imednet.models.variables import Variable
from imednet.workflows.record_update import RecordUpdateWorkflow


def test_create_or_update_records_no_wait() -> None:
    sdk = MagicMock()
    sdk._async_client = None
    job = Job(jobId="1", batchId="1", state="PROCESSING")
    sdk.records.create.return_value = job

    wf = RecordUpdateWorkflow(sdk)
    result = wf.create_or_update_records("STUDY", [{"a": 1}])

    sdk.records.create.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    assert result == job


def test_create_or_update_records_wait_for_completion(monkeypatch) -> None:
    sdk = MagicMock()
    sdk._async_client = None
    initial_job = Job(jobId="1", batchId="1", state="PROCESSING")
    completed_job = Job(jobId="1", batchId="1", state="COMPLETED")
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
    sdk._async_client = None
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
    sdk._async_client = None
    var = Variable(
        studyKey="STUDY",
        variableId=1,
        sequence=1,
        revision=1,
        disabled=False,
        variableOid="VAR1",
        deleted=False,
        formName="Form 1",
        label="Age",
        blinded=False,
        variableName="age",
        variableType="integer",
        formId=1,
        formKey="F1",
    )
    sdk.variables.list.return_value = [var]
    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValidationError):
        wf.create_or_update_records("STUDY", [{"formKey": "F1", "data": {"bad": 1}}])
    sdk.records.create.assert_not_called()

    sdk.records.create.return_value = Job(jobId="1", batchId="1", state="PROCESSING")
    wf.create_or_update_records("STUDY", [{"formKey": "F1", "data": {"age": 5}}])
    sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)
    sdk.records.create.assert_called_once_with(
        "STUDY", [{"formKey": "F1", "data": {"age": 5}}], schema=wf._schema
    )


def test_register_subject_builds_payload() -> None:
    sdk = MagicMock()
    # Mock _async_client to prevent SchemaValidator from being async if not intended
    sdk._async_client = None

    wf = RecordUpdateWorkflow(sdk)
    wf.create_or_update_records = MagicMock(return_value="job")  # type: ignore[method-assign]

    result = wf.register_subject(
        "STUDY",
        form_identifier="F1",
        site_identifier="SITE1",
        data={"x": 1},
        site_identifier_type="name",  # Default
    )

    wf.create_or_update_records.assert_called_once()
    call_kwargs = wf.create_or_update_records.call_args.kwargs
    assert call_kwargs["records_data"] == [
        {
            "formKey": "F1",
            "siteName": "SITE1",
            "data": {"x": 1},
        }
    ]
    assert result == "job"


def test_register_subject_with_site_id() -> None:
    sdk = MagicMock()
    sdk._async_client = None
    wf = RecordUpdateWorkflow(sdk)
    wf.create_or_update_records = MagicMock(return_value="job")  # type: ignore[method-assign]

    result = wf.register_subject(
        "STUDY",
        form_identifier="F1",
        site_identifier=123,
        data={"x": 1},
        site_identifier_type="id",
    )

    wf.create_or_update_records.assert_called_once()
    call_kwargs = wf.create_or_update_records.call_args.kwargs
    assert call_kwargs["records_data"] == [
        {
            "formKey": "F1",
            "siteId": 123,
            "data": {"x": 1},
        }
    ]
    assert result == "job"


def test_create_new_record_builds_payload() -> None:
    sdk = MagicMock()
    sdk._async_client = None
    wf = RecordUpdateWorkflow(sdk)
    wf.create_or_update_records = MagicMock(return_value="job")  # type: ignore[method-assign]

    result = wf.create_new_record(
        "STUDY",
        form_identifier="F1",
        subject_identifier="SUBJ1",
        data={"x": 1},
        subject_identifier_type="key",  # Default
    )

    wf.create_or_update_records.assert_called_once()
    call_kwargs = wf.create_or_update_records.call_args.kwargs
    assert call_kwargs["records_data"] == [
        {
            "formKey": "F1",
            "subjectKey": "SUBJ1",
            "data": {"x": 1},
        }
    ]
    assert result == "job"


def test_create_new_record_with_subject_oid() -> None:
    sdk = MagicMock()
    sdk._async_client = None
    wf = RecordUpdateWorkflow(sdk)
    wf.create_or_update_records = MagicMock(return_value="job")  # type: ignore[method-assign]

    result = wf.create_new_record(
        "STUDY",
        form_identifier="F1",
        subject_identifier="OID1",
        data={"x": 1},
        subject_identifier_type="oid",
    )

    wf.create_or_update_records.assert_called_once()
    call_kwargs = wf.create_or_update_records.call_args.kwargs
    assert call_kwargs["records_data"] == [
        {
            "formKey": "F1",
            "subjectOid": "OID1",
            "data": {"x": 1},
        }
    ]
    assert result == "job"


def test_invalid_subject_identifier_type_raises_keyerror() -> None:
    sdk = MagicMock()
    sdk._async_client = None
    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(KeyError):
        wf.create_new_record(
            "STUDY",
            form_identifier="F1",
            subject_identifier="SUBJ1",
            data={"x": 1},
            subject_identifier_type="invalid_type",  # type: ignore
        )


def test_invalid_site_identifier_type_raises_keyerror() -> None:
    sdk = MagicMock()
    sdk._async_client = None
    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(KeyError):
        wf.register_subject(
            "STUDY",
            form_identifier="F1",
            site_identifier="SITE1",
            data={"x": 1},
            site_identifier_type="invalid_type",  # type: ignore
        )


def test_update_scheduled_record_invalid_interval_identifier_type() -> None:
    sdk = MagicMock()
    sdk._async_client = None
    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(KeyError):
        wf.update_scheduled_record(
            "STUDY",
            form_identifier="F1",
            subject_identifier="SUBJ1",
            interval_identifier="INT1",
            data={"x": 1},
            interval_identifier_type="invalid_type",  # type: ignore
        )


def test_create_or_update_records_form_not_found() -> None:
    sdk = MagicMock()
    sdk._async_client = None
    sdk.variables.list.return_value = []  # no variables found
    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Form key 'F_UNKNOWN' not found"):
        wf.create_or_update_records("STUDY", [{"formKey": "F_UNKNOWN", "data": {"age": 5}}])


def test_create_or_update_records_no_batch_id() -> None:
    sdk = MagicMock()
    sdk._async_client = None

    # Needs a variable to find the form
    var = Variable(
        studyKey="STUDY",
        variableId=1,
        sequence=1,
        revision=1,
        disabled=False,
        variableOid="VAR1",
        deleted=False,
        formName="Form 1",
        label="Age",
        blinded=False,
        variableName="a",
        variableType="integer",
        formId=1,
        formKey="F1",
    )
    sdk.variables.list.return_value = [var]

    # Return a job that has no batch_id
    sdk.records.create.return_value = Job(jobId="1", batchId=None, state="PROCESSING")  # type: ignore[arg-type]

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Submission successful but no batch_id received."):
        wf.create_or_update_records(
            "STUDY", [{"formKey": "F1", "data": {"a": 1}}], wait_for_completion=True
        )


def test_create_or_update_records_empty_records() -> None:
    sdk = MagicMock()
    sdk._async_client = None

    # Return a job that has no batch_id
    sdk.records.create.return_value = Job(jobId="1", batchId="123", state="PROCESSING")

    wf = RecordUpdateWorkflow(sdk)

    wf.create_or_update_records("STUDY", [], wait_for_completion=False)


@pytest.mark.asyncio
async def test_async_create_or_update_records_form_not_found() -> None:
    sdk = MagicMock()
    sdk._async_client = MagicMock()
    sdk.variables.list.return_value = []  # no variables found

    wf = RecordUpdateWorkflow(sdk)
    # mock refresh so it doesn't try to use the SDK un-mocked correctly
    wf._validator.refresh = AsyncMock()  # type: ignore[method-assign]

    with pytest.raises(ValueError, match="Form key 'F_UNKNOWN' not found"):
        await wf.async_create_or_update_records(
            "STUDY", [{"formKey": "F_UNKNOWN", "data": {"age": 5}}]
        )


@pytest.mark.asyncio
async def test_async_create_or_update_records_wait_for_completion(monkeypatch) -> None:
    sdk = MagicMock()
    sdk._async_client = MagicMock()

    initial_job = Job(jobId="1", batchId="1", state="PROCESSING")
    completed_job = Job(jobId="1", batchId="1", state="COMPLETED")
    sdk.records.async_create = AsyncMock(return_value=initial_job)
    sdk.jobs.async_get = AsyncMock(side_effect=[initial_job, completed_job])

    wf = RecordUpdateWorkflow(sdk)

    wf._validator.refresh = AsyncMock()  # type: ignore[method-assign]
    wf._validator.validate_batch = AsyncMock()  # type: ignore[method-assign]

    # Just mock variables_for_form to return something so we skip the refresh and raise
    wf._schema.variables_for_form = MagicMock(return_value=["var_a"])  # type: ignore[method-assign]

    # patch asyncio.sleep to avoid delay
    async def mock_sleep(*args, **kwargs):
        pass

    monkeypatch.setattr("asyncio.sleep", mock_sleep)

    result = await wf.async_create_or_update_records(
        "STUDY",
        [{"formKey": "F1", "data": {"a": 1}}],
        wait_for_completion=True,
        poll_interval=0,
        timeout=5,
    )

    sdk.records.async_create.assert_called_once_with(
        "STUDY", [{"formKey": "F1", "data": {"a": 1}}], schema=wf._schema
    )
    sdk.jobs.async_get.assert_called_with("STUDY", "1")
    assert result.state == "COMPLETED"


@pytest.mark.asyncio
async def test_async_create_or_update_records_no_wait_for_completion() -> None:
    sdk = MagicMock()
    sdk._async_client = MagicMock()

    initial_job = Job(jobId="1", batchId="1", state="PROCESSING")
    sdk.records.async_create = AsyncMock(return_value=initial_job)

    wf = RecordUpdateWorkflow(sdk)

    wf._validator.refresh = AsyncMock()  # type: ignore[method-assign]
    wf._validator.validate_batch = AsyncMock()  # type: ignore[method-assign]

    # Just mock variables_for_form to return something so we skip the refresh and raise
    wf._schema.variables_for_form = MagicMock(return_value=["var_a"])  # type: ignore[method-assign]

    result = await wf.async_create_or_update_records(
        "STUDY",
        [{"formKey": "F1", "data": {"a": 1}}],
        wait_for_completion=False,
    )

    sdk.records.async_create.assert_called_once_with(
        "STUDY", [{"formKey": "F1", "data": {"a": 1}}], schema=wf._schema
    )
    assert result.state == "PROCESSING"
