import types
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
    from typing import Any, cast

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
