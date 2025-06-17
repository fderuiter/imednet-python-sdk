from unittest.mock import AsyncMock, MagicMock

import pytest
from imednet.core.exceptions import ValidationError
from imednet.models.variables import Variable
from imednet.validation.async_schema import AsyncSchemaValidator


def _build_sdk(variable: Variable) -> MagicMock:
    sdk = MagicMock()
    sdk.variables.async_list = AsyncMock(return_value=[variable])
    return sdk


@pytest.mark.asyncio
async def test_validate_record_unknown_variable() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var)
    validator = AsyncSchemaValidator(sdk)

    with pytest.raises(ValidationError):
        await validator.validate_record("STUDY", {"formKey": "F1", "data": {"bad": 1}})

    sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)


@pytest.mark.asyncio
async def test_validate_record_wrong_type() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var)
    validator = AsyncSchemaValidator(sdk)

    with pytest.raises(ValidationError):
        await validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": "x"}})

    sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)


@pytest.mark.asyncio
async def test_refresh_called_when_form_not_cached() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var)
    validator = AsyncSchemaValidator(sdk)
    validator.refresh = AsyncMock(wraps=validator.refresh)  # type: ignore[assignment]

    await validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})

    validator.refresh.assert_awaited_once_with("STUDY")
    sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)


@pytest.mark.asyncio
async def test_validate_record_cached() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var)
    validator = AsyncSchemaValidator(sdk)
    validator.schema._form_variables["F1"] = {"age": var}

    await validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})

    sdk.variables.async_list.assert_not_awaited()
