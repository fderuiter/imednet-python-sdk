from unittest.mock import MagicMock

import pytest

from imednet.errors import ValidationError
from imednet.models.jobs import Job
from imednet.models.variables import Variable
from imednet.workflows.record_update import RecordUpdateWorkflow


def test_create_or_update_records_no_wait() -> None:
    sdk = MagicMock()
    sdk._async_client = None
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.create.return_value = job

    wf = RecordUpdateWorkflow(sdk)
    result = wf.create_or_update_records("STUDY", [{"a": 1}])

    sdk.records.create.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    assert result == job


def test_create_or_update_records_wait_for_completion(monkeypatch) -> None:
    sdk = MagicMock()
    sdk._async_client = None
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


def test_register_subject_builds_payload() -> None:
    sdk = MagicMock()
    # Mock _async_client to prevent SchemaValidator from being async if not intended
    sdk._async_client = None

    wf = RecordUpdateWorkflow(sdk)
    wf.create_or_update_records = MagicMock(return_value="job")

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
    wf.create_or_update_records = MagicMock(return_value="job")

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
    wf.create_or_update_records = MagicMock(return_value="job")

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
    wf.create_or_update_records = MagicMock(return_value="job")

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


def test_create_or_update_records_wait_for_completion_no_batch_id() -> None:
    sdk = MagicMock()
    sdk._async_client = None

    # Return a job with no batch_id
    job = Job(batch_id="", state="PROCESSING")
    sdk.records.create.return_value = job

    # Provide variable so form validation passes
    var = Variable(variable_name="a", variable_type="integer", form_id=1, form_key="F1")
    sdk.variables.list.return_value = [var]

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Submission successful but no batch_id received."):
        wf.create_or_update_records(
            "STUDY",
            [{"formKey": "F1", "data": {"a": 1}}],
            wait_for_completion=True,
        )


def test_create_or_update_records_form_key_not_found() -> None:
    sdk = MagicMock()
    sdk._async_client = None

    # Return empty list for variables so the form key is not found even after refresh
    sdk.variables.list.return_value = []

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Form key 'UNKNOWN_FORM' not found"):
        wf.create_or_update_records(
            "STUDY",
            [{"formKey": "UNKNOWN_FORM", "data": {"a": 1}}],
        )


from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_async_create_or_update_records_no_wait() -> None:
    sdk = MagicMock()
    sdk._async_client = True
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.async_create = AsyncMock(return_value=job)

    wf = RecordUpdateWorkflow(sdk)
    result = await wf.async_create_or_update_records("STUDY", [{"a": 1}])

    sdk.records.async_create.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    assert result == job


@pytest.mark.asyncio
async def test_async_create_or_update_records_wait_for_completion(monkeypatch) -> None:
    sdk = MagicMock()
    sdk._async_client = True
    initial_job = Job(batch_id="1", state="PROCESSING")
    completed_job = Job(batch_id="1", state="COMPLETED")
    sdk.records.async_create = AsyncMock(return_value=initial_job)
    sdk.jobs.async_get = AsyncMock(side_effect=[initial_job, completed_job])

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

    sdk.records.async_create.assert_called_once_with("STUDY", [{"a": 1}], schema=wf._schema)
    sdk.jobs.async_get.assert_called_with("STUDY", "1")
    assert result.state == "COMPLETED"


@pytest.mark.asyncio
async def test_async_create_or_update_records_validation() -> None:
    sdk = MagicMock()
    sdk._async_client = True
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk.variables.async_list = AsyncMock(return_value=[var])
    sdk.records.async_create = AsyncMock()

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValidationError):
        await wf.async_create_or_update_records("STUDY", [{"formKey": "F1", "data": {"bad": 1}}])
    sdk.records.async_create.assert_not_called()

    sdk.records.async_create.return_value = Job(batch_id="1", state="PROCESSING")
    await wf.async_create_or_update_records("STUDY", [{"formKey": "F1", "data": {"age": 5}}])
    sdk.variables.async_list.assert_called_once_with(study_key="STUDY", refresh=True)
    sdk.records.async_create.assert_called_once_with(
        "STUDY", [{"formKey": "F1", "data": {"age": 5}}], schema=wf._schema
    )


@pytest.mark.asyncio
async def test_async_create_or_update_records_wait_for_completion_no_batch_id() -> None:
    sdk = MagicMock()
    sdk._async_client = True
    job = Job(batch_id="", state="PROCESSING")
    sdk.records.async_create = AsyncMock(return_value=job)
    var = Variable(variable_name="a", variable_type="integer", form_id=1, form_key="F1")
    sdk.variables.async_list = AsyncMock(return_value=[var])

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Submission successful but no batch_id received."):
        await wf.async_create_or_update_records(
            "STUDY",
            [{"formKey": "F1", "data": {"a": 1}}],
            wait_for_completion=True,
        )


@pytest.mark.asyncio
async def test_async_create_or_update_records_form_key_not_found() -> None:
    sdk = MagicMock()
    sdk._async_client = True
    sdk.variables.async_list = AsyncMock(return_value=[])

    wf = RecordUpdateWorkflow(sdk)

    with pytest.raises(ValueError, match="Form key 'UNKNOWN_FORM' not found"):
        await wf.async_create_or_update_records(
            "STUDY",
            [{"formKey": "UNKNOWN_FORM", "data": {"a": 1}}],
        )
