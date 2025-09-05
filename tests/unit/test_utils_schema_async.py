from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.api.core.exceptions import ValidationError
from imednet.api.models.forms import Form
from imednet.api.models.variables import Variable
from imednet.validation.cache import SchemaValidator


def _make_var(name: str, form_id: int = 1, form_key: str = "F1") -> Variable:
    return Variable(variable_name=name, variable_type="integer", form_id=form_id, form_key=form_key)


@pytest.mark.asyncio
async def test_async_schema_cache_refresh() -> None:
    forms = MagicMock()
    forms.list.return_value = [Form(form_id=1, form_key="F1")]
    variables = MagicMock()
    var = _make_var("age")
    variables.async_list = AsyncMock(return_value=[var])

    sdk = MagicMock()
    sdk.forms = forms
    sdk.variables = variables
    validator = SchemaValidator(sdk)

    await validator.schema.refresh(forms, variables, study_key="ST")

    assert validator.schema.form_key_from_id(1) == "F1"
    assert validator.schema.variables_for_form("F1")["age"] is var
    variables.async_list.assert_awaited_once_with(study_key="ST", refresh=True)


@pytest.mark.asyncio
async def test_validate_record_and_batch_async() -> None:
    var = _make_var("age")
    sdk = MagicMock()
    sdk.variables.async_list = AsyncMock(return_value=[var])
    validator = SchemaValidator(sdk)

    record = {"formKey": "F1", "data": {"age": 1}}
    await validator.validate_record("ST", record)
    sdk.variables.async_list.assert_awaited_once_with(study_key="ST", refresh=True)

    validator.validate_record = AsyncMock()  # type: ignore[assignment]
    await validator.validate_batch("ST", [record, record])
    assert validator.validate_record.await_count == 2


@pytest.mark.asyncio
async def test_unknown_form_refreshes_and_raises() -> None:
    var = _make_var("age")
    sdk = MagicMock()
    sdk.variables.async_list = AsyncMock(return_value=[var])
    validator = SchemaValidator(sdk)

    with pytest.raises(ValidationError, match="Unknown form BAD"):
        await validator.validate_record("ST", {"formKey": "BAD", "data": {}})
    sdk.variables.async_list.assert_awaited_once_with(study_key="ST", refresh=True)
