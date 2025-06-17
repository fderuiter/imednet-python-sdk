import types
from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from imednet.core.exceptions import ValidationError
from imednet.models.jobs import Job
from imednet.models.variables import Variable
from imednet.testing import fake_data
from imednet.validation.schema import SchemaCache
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

    cache = SchemaCache()
    cache.refresh(cast(Any, forms_ep), cast(Any, vars_ep), study_key="S")
    return cache, var


def test_create_or_update_records_no_wait(schema: SchemaCache) -> None:
    sdk = MagicMock()
    job = Job(batch_id="1", state="PROCESSING")
    sdk.records.create.return_value = job

    wf = RecordUpdateWorkflow(sdk)
    wf._validator.schema = schema
    wf._schema = schema
    record = fake_data.fake_record(schema)
    result = wf.create_or_update_records("S", [record])

    sdk.records.create.assert_called_once_with("S", [record], schema=schema)
    assert result == job


def test_create_or_update_records_validation() -> None:
    schema, var = _build_schema()
    sdk = MagicMock()
    wf = RecordUpdateWorkflow(sdk)
    wf._validator.schema = schema
    wf._schema = schema

    with pytest.raises(ValidationError):
        wf.create_or_update_records("S", [{"formKey": var.form_key, "data": {}}])
    sdk.records.create.assert_not_called()

    sdk.records.create.return_value = Job(batch_id="1", state="PROCESSING")
    wf.create_or_update_records("S", [{"formKey": var.form_key, "data": {var.variable_name: 5}}])
    sdk.records.create.assert_called_once_with(
        "S",
        [{"formKey": var.form_key, "data": {var.variable_name: 5}}],
        schema=schema,
    )


def test_register_subject() -> None:
    wf = RecordUpdateWorkflow(MagicMock())
    mock: MagicMock = MagicMock(return_value=Job(batch_id="1", state="PROCESSING"))
    cast(Any, wf).create_or_update_records = mock
    wf.register_subject(
        study_key="S",
        form_identifier="REG",
        site_identifier="SITE",
        data={"f": 1},
    )
    mock.assert_called_once_with(
        study_key="S",
        records_data=[{"formKey": "REG", "siteName": "SITE", "data": {"f": 1}}],
        wait_for_completion=False,
        timeout=300,
        poll_interval=5,
    )


def test_update_scheduled_record() -> None:
    wf = RecordUpdateWorkflow(MagicMock())
    mock: MagicMock = MagicMock(return_value=Job(batch_id="1", state="PROCESSING"))
    cast(Any, wf).create_or_update_records = mock
    wf.update_scheduled_record(
        study_key="S",
        form_identifier="FORM",
        subject_identifier="SUBJ",
        interval_identifier="VISIT1",
        data={"v": 2},
    )
    mock.assert_called_once_with(
        study_key="S",
        records_data=[
            {
                "formKey": "FORM",
                "subjectKey": "SUBJ",
                "intervalName": "VISIT1",
                "data": {"v": 2},
            }
        ],
        wait_for_completion=False,
        timeout=300,
        poll_interval=5,
    )


def test_create_new_record_method() -> None:
    wf = RecordUpdateWorkflow(MagicMock())
    mock: MagicMock = MagicMock(return_value=Job(batch_id="1", state="PROCESSING"))
    cast(Any, wf).create_or_update_records = mock
    wf.create_new_record(
        study_key="S",
        form_identifier="FORM",
        subject_identifier="SUBJ",
        data={"v": 3},
    )
    mock.assert_called_once_with(
        study_key="S",
        records_data=[{"formKey": "FORM", "subjectKey": "SUBJ", "data": {"v": 3}}],
        wait_for_completion=False,
        timeout=300,
        poll_interval=5,
    )
