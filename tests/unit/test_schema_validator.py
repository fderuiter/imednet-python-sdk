import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from imednet.errors import ValidationError
from imednet.models.variables import Variable
from imednet.validation.cache import AsyncSchemaValidator, SchemaValidator


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
    if async_mode:
        validator = AsyncSchemaValidator(sdk)  # type: ignore[assignment]
    else:
        validator = SchemaValidator(sdk)  # type: ignore[assignment]

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
    if async_mode:
        validator = AsyncSchemaValidator(sdk)  # type: ignore[assignment]
    else:
        validator = SchemaValidator(sdk)  # type: ignore[assignment]

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
def test_validate_record_unknown_form(async_mode: bool) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode)
    if async_mode:
        validator = AsyncSchemaValidator(sdk)  # type: ignore[assignment]
    else:
        validator = SchemaValidator(sdk)  # type: ignore[assignment]

    with pytest.raises(ValidationError, match="Unknown form BAD"):
        if async_mode:
            asyncio.run(validator.validate_record("STUDY", {"formKey": "BAD", "data": {}}))
        else:
            validator.validate_record("STUDY", {"formKey": "BAD", "data": {}})

    if async_mode:
        sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)
    else:
        sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)


@pytest.mark.parametrize("async_mode", [False, True])
def test_refresh_called_when_form_not_cached(async_mode: bool) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode)
    if async_mode:
        validator = AsyncSchemaValidator(sdk)  # type: ignore[assignment]
        validator.refresh = AsyncMock(wraps=validator.refresh)  # type: ignore[assignment]
        asyncio.run(validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}}))
        validator.refresh.assert_awaited_once_with("STUDY")
        sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)
    else:
        validator = SchemaValidator(sdk)  # type: ignore[assignment]
        validator.refresh = MagicMock(wraps=validator.refresh)  # type: ignore[assignment]
        validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})
        validator.refresh.assert_called_once_with("STUDY")
        sdk.variables.list.assert_called_once_with(study_key="STUDY", refresh=True)


@pytest.mark.parametrize("async_mode", [False, True])
def test_validate_record_cached(async_mode: bool) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode)
    if async_mode:
        validator = AsyncSchemaValidator(sdk)  # type: ignore[assignment]
    else:
        validator = SchemaValidator(sdk)  # type: ignore[assignment]

    validator.schema._form_variables["F1"] = {"age": var}

    if async_mode:
        asyncio.run(validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}}))
        sdk.variables.async_list.assert_not_awaited()
    else:
        validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})
        sdk.variables.list.assert_not_called()


@pytest.mark.parametrize("async_mode", [False, True])
def test_validate_record_with_form_id_fallback(async_mode: bool) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=123, form_key="F1")
    sdk = _build_sdk(var, async_mode)
    if async_mode:
        validator = AsyncSchemaValidator(sdk)  # type: ignore[assignment]
    else:
        validator = SchemaValidator(sdk)  # type: ignore[assignment]

    validator.schema._form_variables["F1"] = {"age": var}
    validator.schema._form_id_to_key[123] = "F1"

    if async_mode:
        asyncio.run(validator.validate_record("STUDY", {"formId": 123, "data": {"age": 1}}))
        sdk.variables.async_list.assert_not_awaited()
    else:
        validator.validate_record("STUDY", {"formId": 123, "data": {"age": 1}})
        sdk.variables.list.assert_not_called()


@pytest.mark.parametrize("async_mode", [False, True])
def test_validate_record_missing_form_identifier(async_mode: bool) -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode)
    if async_mode:
        validator = AsyncSchemaValidator(sdk)  # type: ignore[assignment]
    else:
        validator = SchemaValidator(sdk)  # type: ignore[assignment]

    validator.schema._form_variables["F1"] = {"age": var}

    # Missing formKey and formId entirely should just skip validation without error
    if async_mode:
        asyncio.run(validator.validate_record("STUDY", {"data": {"age": "bad"}}))
        sdk.variables.async_list.assert_not_awaited()
    else:
        validator.validate_record("STUDY", {"data": {"age": "bad"}})
        sdk.variables.list.assert_not_called()


def test_schema_validator_is_async_deprecation_warning() -> None:
    sdk = MagicMock()
    with pytest.warns(
        DeprecationWarning, match="Passing `is_async=True` to SchemaValidator is deprecated"
    ):
        validator = SchemaValidator(sdk, is_async=True)

    assert isinstance(validator, AsyncSchemaValidator)


def test_schema_validator_is_async_positional_deprecation_warning() -> None:
    sdk = MagicMock()
    with pytest.warns(
        DeprecationWarning, match="Passing `is_async=True` to SchemaValidator is deprecated"
    ):
        validator = SchemaValidator(sdk, True)

    assert isinstance(validator, AsyncSchemaValidator)


def test_validate_record_with_none_value_does_not_raise() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode=False)
    validator = SchemaValidator(sdk)
    validator.schema._form_variables["F1"] = {"age": var}

    # This should not raise an exception
    validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": None}})


def test_check_type_unknown_variable_type() -> None:
    var = Variable(variable_name="age", variable_type="unknown_type", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode=False)
    validator = SchemaValidator(sdk)
    validator.schema._form_variables["F1"] = {"age": var}

    from imednet.errors import UnknownVariableTypeError

    with pytest.raises(UnknownVariableTypeError, match="unknown_type"):
        validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})


def test_check_type_case_insensitive_type() -> None:
    var = Variable(variable_name="age", variable_type="InTeGeR", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode=False)
    validator = SchemaValidator(sdk)
    validator.schema._form_variables["F1"] = {"age": var}

    # This should pass without error due to lowercasing fallback
    validator.validate_record("STUDY", {"formKey": "F1", "data": {"age": 1}})


def test_validate_record_entry_with_form_key() -> None:
    from imednet.validation.cache import SchemaCache, validate_record_entry

    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    schema = SchemaCache()
    schema.populate([var])

    # Should not raise
    validate_record_entry(schema, {"form_key": "F1", "data": {"age": 1}})


def test_validate_record_entry_with_form_id() -> None:
    from imednet.validation.cache import SchemaCache, validate_record_entry

    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    schema = SchemaCache()
    schema.populate([var])

    # Should not raise
    validate_record_entry(schema, {"form_id": 1, "data": {"age": 1}})


def test_validate_record_entry_missing_both() -> None:
    from imednet.validation.cache import SchemaCache, validate_record_entry

    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    schema = SchemaCache()
    schema.populate([var])

    # Should not raise, just skips validation
    validate_record_entry(schema, {"data": {"age": 1}})


def test_type_validators_coverage() -> None:
    from imednet.validation.cache import (
        ValidationError,
        _validate_bool,
        _validate_float,
        _validate_int,
        _validate_text,
    )

    with pytest.raises(ValidationError, match="must be an integer"):
        _validate_int("1")
    with pytest.raises(ValidationError, match="must be numeric"):
        _validate_float("1.0")
    with pytest.raises(ValidationError, match="must be boolean"):
        _validate_bool(1)
    with pytest.raises(ValidationError, match="must be a string"):
        _validate_text(1)


def test_validate_batch_coverage() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode=False)
    validator = SchemaValidator(sdk)
    validator.schema._form_variables["F1"] = {"age": var}

    # Should not raise
    validator.validate_batch(
        "STUDY", [{"formKey": "F1", "data": {"age": 1}}, {"formKey": "F1", "data": {"age": 2}}]
    )


def test_async_validate_batch_coverage() -> None:
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    sdk = _build_sdk(var, async_mode=True)
    validator = AsyncSchemaValidator(sdk)
    validator.schema._form_variables["F1"] = {"age": var}

    # Should not raise
    asyncio.run(
        validator.validate_batch(
            "STUDY", [{"formKey": "F1", "data": {"age": 1}}, {"formKey": "F1", "data": {"age": 2}}]
        )
    )


def test_schema_cache_forms_property() -> None:
    from imednet.validation.cache import SchemaCache

    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    cache = SchemaCache()
    cache.populate([var])

    assert "F1" in cache.forms
    assert "age" in cache.forms["F1"]


def test_base_schema_cache_refresh() -> None:
    from unittest.mock import MagicMock

    from imednet.validation.cache import SchemaCache

    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")

    cache = SchemaCache()
    forms = MagicMock()
    variables = MagicMock()
    variables.list.return_value = [var]

    cache.refresh(forms, variables, "STUDY")
    variables.list.assert_called_once_with(study_key="STUDY", refresh=True)
    assert "F1" in cache.forms


@pytest.mark.asyncio
async def test_base_schema_cache_async_refresh() -> None:
    from unittest.mock import AsyncMock, MagicMock

    from imednet.validation.cache import AsyncSchemaCache

    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")

    cache = AsyncSchemaCache()
    forms = MagicMock()
    variables = MagicMock()
    variables.async_list = AsyncMock(return_value=[var])

    await cache.refresh(forms, variables, "STUDY")
    variables.async_list.assert_awaited_once_with(study_key="STUDY", refresh=True)
    assert "F1" in cache.forms
