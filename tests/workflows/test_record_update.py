import asyncio
import types
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.core.exceptions import ValidationError
from imednet.models.jobs import Job
from imednet.models.variables import Variable
from imednet.testing import fake_data
from imednet.validation.cache import SchemaCache
from imednet.workflows.record_update import RecordUpdateWorkflow


def _build_schema() -> tuple[SchemaCache, Variable]:
    forms = fake_data.fake_forms_for_cache(1, study_key="S")
    variables = fake_data.fake_variables_for_cache(forms, vars_per_form=1, study_key="S")
    var = variables[0]
    object.__setattr__(var, "required", True)
    var.variable_type = "integer"
    forms_ep = types.SimpleNamespace(list=lambda **_: forms)

    def list_vars(*_, form_id=None, **__):
        return [v for v in variables if form_id is None or v.form_id == form_id]

    vars_ep = types.SimpleNamespace(list=list_vars)
    from typing import Any, cast

    cache = SchemaCache()
    cache.refresh(cast(Any, forms_ep), cast(Any, vars_ep), study_key="S")
    return cache, var


@pytest.mark.parametrize("async_mode", [False, True])
def test_create_or_update_records_no_wait(schema: SchemaCache, async_mode: bool) -> None:
    sdk = MagicMock()
    job = Job(batch_id="1", state="PROCESSING")
    if async_mode:
        sdk._async_client = object()
        sdk.records.async_create = AsyncMock(return_value=job)
    else:
        sdk.records.create = MagicMock(return_value=job)

    wf = RecordUpdateWorkflow(sdk)
    wf._validator.schema = schema
    wf._schema = schema
    record = fake_data.fake_record(schema)

    if async_mode:
        result = asyncio.run(wf.async_create_or_update_records("S", [record]))
        sdk.records.async_create.assert_awaited_once_with("S", [record], schema=schema)
    else:
        result = wf.create_or_update_records("S", [record])
        sdk.records.create.assert_called_once_with("S", [record], schema=schema)
    assert result == job


@pytest.mark.parametrize("async_mode", [False, True])
def test_create_or_update_records_validation(async_mode: bool) -> None:
    schema, var = _build_schema()
    sdk = MagicMock()
    if async_mode:
        sdk._async_client = object()
        sdk.records.async_create = AsyncMock(return_value=Job(batch_id="1", state="PROCESSING"))
    else:
        sdk.records.create = MagicMock(return_value=Job(batch_id="1", state="PROCESSING"))

    wf = RecordUpdateWorkflow(sdk)
    wf._validator.schema = schema
    wf._schema = schema

    with pytest.raises(ValidationError):
        if async_mode:
            asyncio.run(
                wf.async_create_or_update_records("S", [{"formKey": var.form_key, "data": {}}])
            )
        else:
            wf.create_or_update_records("S", [{"formKey": var.form_key, "data": {}}])
    if async_mode:
        sdk.records.async_create.assert_not_awaited()
    else:
        sdk.records.create.assert_not_called()

    if async_mode:
        asyncio.run(
            wf.async_create_or_update_records(
                "S", [{"formKey": var.form_key, "data": {var.variable_name: 5}}]
            )
        )
        sdk.records.async_create.assert_awaited_once_with(
            "S",
            [{"formKey": var.form_key, "data": {var.variable_name: 5}}],
            schema=schema,
        )
    else:
        wf.create_or_update_records(
            "S", [{"formKey": var.form_key, "data": {var.variable_name: 5}}]
        )
        sdk.records.create.assert_called_once_with(
            "S",
            [{"formKey": var.form_key, "data": {var.variable_name: 5}}],
            schema=schema,
        )


@pytest.mark.parametrize("async_mode", [False, True])
def test_create_or_update_records_unknown_form_key(async_mode: bool) -> None:
    sdk = MagicMock()
    if async_mode:
        sdk._async_client = object()
        sdk.records.async_create = AsyncMock()
    else:
        sdk.records.create = MagicMock()

    wf = RecordUpdateWorkflow(sdk)
    schema = SchemaCache()
    wf._validator.schema = schema
    wf._schema = schema

    if async_mode:
        wf._validator.refresh = AsyncMock()  # type: ignore[method-assign]
        wf._validator.validate_batch = AsyncMock()  # type: ignore[method-assign]
        with pytest.raises(ValueError, match="Form key 'F1' not found"):
            asyncio.run(wf.async_create_or_update_records("S", [{"formKey": "F1", "data": {}}]))
        wf._validator.refresh.assert_awaited_once_with("S")
        wf._validator.validate_batch.assert_not_called()
        sdk.records.async_create.assert_not_awaited()
    else:
        wf._validator.refresh = MagicMock()  # type: ignore[method-assign]
        wf._validator.validate_batch = MagicMock()  # type: ignore[method-assign]
        with pytest.raises(ValueError, match="Form key 'F1' not found"):
            wf.create_or_update_records("S", [{"formKey": "F1", "data": {}}])
        wf._validator.refresh.assert_called_once_with("S")
        wf._validator.validate_batch.assert_not_called()
        sdk.records.create.assert_not_called()


@pytest.mark.parametrize("async_mode", [False, True])
def test_create_or_update_records_refresh_and_validate(async_mode: bool) -> None:
    sdk = MagicMock()
    job = Job(batch_id="1", state="PROCESSING")
    if async_mode:
        sdk._async_client = object()
        sdk.records.async_create = AsyncMock(return_value=job)
        sdk.variables.async_list = AsyncMock(
            return_value=[
                Variable(
                    variable_name="age",
                    variable_type="integer",
                    form_id=1,
                    form_key="F1",
                )
            ]
        )
    else:
        sdk.records.create = MagicMock(return_value=job)
        sdk.variables.list = MagicMock(
            return_value=[
                Variable(
                    variable_name="age",
                    variable_type="integer",
                    form_id=1,
                    form_key="F1",
                )
            ]
        )

    wf = RecordUpdateWorkflow(sdk)
    if async_mode:
        wf._validator.validate_batch = AsyncMock()  # type: ignore[method-assign]
        asyncio.run(
            wf.async_create_or_update_records("STUDY", [{"formKey": "F1", "data": {"age": 5}}])
        )
        sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)
        wf._validator.validate_batch.assert_awaited_once_with(
            "STUDY",
            [{"formKey": "F1", "data": {"age": 5}}],
        )
        sdk.records.async_create.assert_awaited_once_with(
            "STUDY",
            [{"formKey": "F1", "data": {"age": 5}}],
            schema=wf._schema,
        )
    else:
        wf._validator.validate_batch = MagicMock()  # type: ignore[method-assign]
        wf.create_or_update_records("STUDY", [{"formKey": "F1", "data": {"age": 5}}])
        sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)
        wf._validator.validate_batch.assert_called_once_with(
            "STUDY",
            [{"formKey": "F1", "data": {"age": 5}}],
        )
        sdk.records.create.assert_called_once_with(
            "STUDY",
            [{"formKey": "F1", "data": {"age": 5}}],
            schema=wf._schema,
        )


@pytest.mark.parametrize("async_mode", [False, True])
def test_create_or_update_records_wait_for_completion(
    async_mode: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    sdk = MagicMock()
    initial_job = Job(batch_id="1", state="PROCESSING")
    completed_job = Job(batch_id="1", state="COMPLETED")
    if async_mode:
        sdk._async_client = object()
        sdk.records.async_create = AsyncMock(return_value=initial_job)
        sdk.jobs.async_get = AsyncMock(side_effect=[initial_job, completed_job])
        sdk.variables.async_list = AsyncMock(
            return_value=[
                Variable(
                    variable_name="age",
                    variable_type="integer",
                    form_id=1,
                    form_key="F1",
                )
            ]
        )
        wf = RecordUpdateWorkflow(sdk)
        wf._validator.validate_batch = AsyncMock()  # type: ignore[method-assign]
        monkeypatch.setattr(asyncio, "sleep", AsyncMock())
        result = asyncio.run(
            wf.async_create_or_update_records(
                "STUDY",
                [{"formKey": "F1", "data": {}}],
                wait_for_completion=True,
                poll_interval=0,
                timeout=5,
            )
        )
        sdk.records.async_create.assert_awaited_once_with(
            "STUDY",
            [{"formKey": "F1", "data": {}}],
            schema=wf._schema,
        )
        sdk.jobs.async_get.assert_awaited_with("STUDY", "1")
    else:
        sdk.records.create = MagicMock(return_value=initial_job)
        sdk.jobs.get = MagicMock(side_effect=[initial_job, completed_job])
        sdk.variables.list = MagicMock(
            return_value=[
                Variable(
                    variable_name="age",
                    variable_type="integer",
                    form_id=1,
                    form_key="F1",
                )
            ]
        )
        wf = RecordUpdateWorkflow(sdk)
        wf._validator.validate_batch = MagicMock()  # type: ignore[method-assign]
        monkeypatch.setattr("time.sleep", lambda *_: None)
        result = wf.create_or_update_records(
            "STUDY",
            [{"formKey": "F1", "data": {}}],
            wait_for_completion=True,
            poll_interval=0,
            timeout=5,
        )
        sdk.records.create.assert_called_once_with(
            "STUDY",
            [{"formKey": "F1", "data": {}}],
            schema=wf._schema,
        )
        sdk.jobs.get.assert_called_with("STUDY", "1")
    assert result.state == "COMPLETED"
