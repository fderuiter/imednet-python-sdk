"""TODO: Add docstring."""
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet import AsyncImednetSDK, ImednetSDK
from imednet.errors import ValidationError
from imednet.models.jobs import Job
from imednet.models.variables import Variable
from imednet_workflows.record_update import RecordUpdateWorkflow


def test_create_or_update_records_no_wait() -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
    job = Job(jobId="1", batchId="1", state="PROCESSING")
    sdk.create_record.return_value = job

    wf = RecordUpdateWorkflow(sdk)
    result = wf.create_or_update_records("STUDY", [{"a": 1}])

    sdk.create_record.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    assert result == job


def test_create_or_update_records_wait_for_completion(monkeypatch) -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
    initial_job = Job(jobId="1", batchId="1", state="PROCESSING")
    completed_job = Job(jobId="1", batchId="1", state="COMPLETED")
    sdk.create_record.return_value = initial_job
    sdk.poll_job.return_value = completed_job

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

    sdk.create_record.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    sdk.poll_job.assert_called_with("STUDY", "1", timeout=5, interval=0)
    assert result.state == "COMPLETED"


def test_update_scheduled_record_builds_payload() -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
    wf = RecordUpdateWorkflow(sdk)
    wf.create_or_update_records = MagicMock(return_value="job")  # type: ignore[method-assign]  # type: ignore[method-assign]

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
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
    var = Variable(
        studyKey="STUDY",
        variableId=1,
        sequence=1,
        revision=1,
        disabled=False,
        variableOid="OID1",
        deleted=False,
        formName="F1",
        label="Label",
        blinded=False,
        variableName="age",
        variableType="integer",
        formId=1,
        formKey="F1",
    )
    sdk.get_variables.return_value = [var]
    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValidationError):
        wf.create_or_update_records("STUDY", [{"formKey": "F1", "data": {"bad": 1}}])
    sdk.records.create.assert_not_called()

    sdk.create_record.return_value = Job(jobId="1", batchId="1", state="PROCESSING")
    wf.create_or_update_records("STUDY", [{"formKey": "F1", "data": {"age": 5}}])
    sdk.get_variables.assert_called_once_with(study_key="STUDY")
    sdk.create_record.assert_called_once_with(
        "STUDY", [{"formKey": "F1", "data": {"age": 5}}], schema=wf._schema
    )


def test_register_subject_builds_payload() -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    # Mock _async_client to prevent SchemaValidator from being async if not intended
    del sdk.async_create_record

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
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
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
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
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
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
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
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
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
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
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
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record
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


def test_create_or_update_records_wait_for_completion_no_batch_id() -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record

    # Return a job with no batch_id
    job = Job(jobId="1", batchId="", state="PROCESSING")
    sdk.create_record.return_value = job

    # Provide variable so form validation passes
    var = Variable(
        studyKey="STUDY",
        variableId=1,
        sequence=1,
        revision=1,
        disabled=False,
        variableOid="OID1",
        deleted=False,
        formName="F1",
        label="Label",
        blinded=False,
        variableName="a",
        variableType="integer",
        formId=1,
        formKey="F1",
    )
    sdk.get_variables.return_value = [var]

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Submission successful but no batch_id received."):
        wf.create_or_update_records(
            "STUDY",
            [{"formKey": "F1", "data": {"a": 1}}],
            wait_for_completion=True,
        )


def test_create_or_update_records_form_key_not_found() -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    del sdk.async_create_record

    # Return empty list for variables so the form key is not found even after refresh
    sdk.get_variables.return_value = []

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Form key 'UNKNOWN_FORM' not found"):
        wf.create_or_update_records(
            "STUDY",
            [{"formKey": "UNKNOWN_FORM", "data": {"a": 1}}],
        )


@pytest.mark.asyncio
async def test_async_create_or_update_records_no_wait() -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    sdk._async_client = True
    job = Job(jobId="1", batchId="1", state="PROCESSING")
    sdk.async_create_record = AsyncMock(return_value=job)

    wf = RecordUpdateWorkflow(sdk)
    result = await wf.async_create_or_update_records("STUDY", [{"a": 1}])

    sdk.async_create_record.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    assert result == job


@pytest.mark.asyncio
async def test_async_create_or_update_records_wait_for_completion(monkeypatch) -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    sdk._async_client = True
    initial_job = Job(jobId="1", batchId="1", state="PROCESSING")
    completed_job = Job(jobId="1", batchId="1", state="COMPLETED")
    sdk.async_create_record = AsyncMock(return_value=initial_job)
    sdk.async_poll_job = AsyncMock(return_value=completed_job)

    wf = RecordUpdateWorkflow(sdk)
    import anyio

    monkeypatch.setattr(anyio, "sleep", AsyncMock())
    result = await wf.async_create_or_update_records(
        "STUDY",
        [{"a": 1}],
        wait_for_completion=True,
        poll_interval=0,
        timeout=5,
    )

    sdk.async_create_record.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    sdk.async_poll_job.assert_called_with("STUDY", "1", timeout=5, interval=0)
    assert result.state == "COMPLETED"


@pytest.mark.asyncio
async def test_async_create_or_update_records_validation() -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    sdk._async_client = True
    var = Variable(
        studyKey="STUDY",
        variableId=1,
        sequence=1,
        revision=1,
        disabled=False,
        variableOid="OID1",
        deleted=False,
        formName="F1",
        label="Label",
        blinded=False,
        variableName="age",
        variableType="integer",
        formId=1,
        formKey="F1",
    )
    sdk.async_get_variables = AsyncMock(return_value=[var])
    sdk.async_create_record = AsyncMock()

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValidationError):
        await wf.async_create_or_update_records("STUDY", [{"formKey": "F1", "data": {"bad": 1}}])
    sdk.async_create_record.assert_not_called()

    sdk.async_create_record = AsyncMock(
        return_value=Job(jobId="1", batchId="1", state="PROCESSING")
    )
    await wf.async_create_or_update_records("STUDY", [{"formKey": "F1", "data": {"age": 5}}])
    sdk.async_get_variables.assert_called_once_with(study_key="STUDY")
    sdk.async_create_record.assert_called_once_with(
        "STUDY", [{"formKey": "F1", "data": {"age": 5}}], schema=wf._schema
    )


@pytest.mark.asyncio
async def test_async_create_or_update_records_wait_for_completion_no_batch_id() -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    sdk._async_client = True
    job = Job(jobId="1", batchId="", state="PROCESSING")
    sdk.async_create_record = AsyncMock(return_value=job)
    var = Variable(
        studyKey="STUDY",
        variableId=1,
        sequence=1,
        revision=1,
        disabled=False,
        variableOid="OID1",
        deleted=False,
        formName="F1",
        label="Label",
        blinded=False,
        variableName="a",
        variableType="integer",
        formId=1,
        formKey="F1",
    )
    sdk.async_get_variables = AsyncMock(return_value=[var])

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Submission successful but no batch_id received."):
        await wf.async_create_or_update_records(
            "STUDY",
            [{"formKey": "F1", "data": {"a": 1}}],
            wait_for_completion=True,
        )


@pytest.mark.asyncio
async def test_async_create_or_update_records_form_key_not_found() -> None:
    """TODO: Add docstring."""
    sdk = MagicMock()
    sdk._async_client = True
    sdk.async_get_variables = AsyncMock(return_value=[])

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Form key 'UNKNOWN_FORM' not found"):
        await wf.async_create_or_update_records(
            "STUDY",
            [{"formKey": "UNKNOWN_FORM", "data": {"a": 1}}],
        )
