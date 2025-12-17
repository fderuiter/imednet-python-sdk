from unittest.mock import AsyncMock

import pytest

import imednet.endpoints.records as records
from imednet.core.exceptions import ValidationError
from imednet.models.variables import Variable
from imednet.validation.cache import SchemaCache


@pytest.fixture
def schema():
    s = SchemaCache()
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    s._form_variables = {"F1": {"age": var}}
    s._form_id_to_key = {1: "F1"}
    return s


@pytest.mark.asyncio
async def test_async_create_validates_data(dummy_client, context, response_factory, schema):
    ep = records.RecordsEndpoint(dummy_client, context, async_client=dummy_client)
    dummy_client.post = AsyncMock(return_value=response_factory({"jobId": "1"}))

    # Validation error: unknown form
    with pytest.raises(ValidationError, match="Unknown form BAD"):
        await ep.async_create("S1", [{"formKey": "BAD", "data": {}}], schema=schema)
    dummy_client.post.assert_not_called()

    # Validation error: invalid data
    with pytest.raises(ValidationError):
        await ep.async_create("S1", [{"formKey": "F1", "data": {"bad": 1}}], schema=schema)
    dummy_client.post.assert_not_called()

    # Valid data
    await ep.async_create("S1", [{"formKey": "F1", "data": {"age": 5}}], schema=schema)
    dummy_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_async_create_validates_data_with_snake_case_keys(
    dummy_client, context, response_factory, schema
):
    ep = records.RecordsEndpoint(dummy_client, context, async_client=dummy_client)
    dummy_client.post = AsyncMock(return_value=response_factory({"jobId": "1"}))

    # Should raise validation error because "bad" is not in schema
    # Even if we use snake_case "form_key"
    with pytest.raises(ValidationError):
        await ep.async_create("S1", [{"form_key": "F1", "data": {"bad": 1}}], schema=schema)


@pytest.mark.asyncio
async def test_async_create_resolves_form_id(dummy_client, context, response_factory, schema):
    ep = records.RecordsEndpoint(dummy_client, context, async_client=dummy_client)
    dummy_client.post = AsyncMock(return_value=response_factory({"jobId": "1"}))

    # Valid data using formId instead of formKey
    await ep.async_create("S1", [{"formId": 1, "data": {"age": 5}}], schema=schema)
    dummy_client.post.assert_called_once()

    # reset mock
    dummy_client.post.reset_mock()

    # Valid data using form_id (snake case)
    await ep.async_create("S1", [{"form_id": 1, "data": {"age": 5}}], schema=schema)
    dummy_client.post.assert_called_once()
