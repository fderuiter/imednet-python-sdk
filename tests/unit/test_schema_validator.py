import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.core.exceptions import ValidationError
from imednet.models.variables import Variable
from imednet.validation.cache import SchemaValidator


def _build_sdk(variable: Variable, async_mode: bool) -> MagicMock:
    sdk = MagicMock()
    if async_mode:
        sdk.variables.async_list = AsyncMock(return_value=[variable])
    else:
        sdk.variables.list.return_value = [variable]
    return sdk


@pytest.mark.parametrize("async_mode", [False, True])
def test_validate_record_unknown_variable(async_mode: bool) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode)
    validator = SchemaValidator(sdk)

    with pytest.raises(ValidationError):
        if async_mode:
            asyncio.run(validator.validate_record("STUDY", {"formKey": "F1", "data": {"bad": 1}}))
        else:
            validator.validate_record("STUDY", {"formKey": "F1", "data": {"bad": 1}})

    if async_mode:
        sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)
    else:
        sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)


@pytest.mark.parametrize("async_mode", [False, True])
def test_validate_record_wrong_type(async_mode: bool) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode)
    validator = SchemaValidator(sdk)

    with pytest.raises(ValidationError):
        if async_mode:
            asyncio.run(validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": "x"}}))
        else:
            validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": "x"}})

    if async_mode:
        sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)
    else:
        sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)


@pytest.mark.parametrize("async_mode", [False, True])
def test_refresh_called_when_form_not_cached(async_mode: bool) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode)
    validator = SchemaValidator(sdk)
    if async_mode:
        validator.refresh = AsyncMock(wraps=validator.refresh)  # type: ignore[assignment]
        asyncio.run(validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}}))
        validator.refresh.assert_awaited_once_with("STUDY")
        sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)
    else:
        validator.refresh = MagicMock(wraps=validator.refresh)  # type: ignore[assignment]
        validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})
        validator.refresh.assert_called_once_with("STUDY")
        sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)


@pytest.mark.parametrize("async_mode", [False, True])
def test_validate_record_cached(async_mode: bool) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode)
    validator = SchemaValidator(sdk)
    validator.schema._form_variables["F1"] = {"age": var}

    if async_mode:
        asyncio.run(validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}}))
        sdk.variables.async_list.assert_not_awaited()
    else:
        validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})
        sdk.variables.list.assert_not_called()
