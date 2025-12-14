import pytest
import inspect
from unittest.mock import AsyncMock

import imednet.endpoints.records as records
from imednet.core.exceptions import ValidationError
from imednet.models.variables import Variable
from imednet.validation.cache import SchemaCache


def test_create_validates_using_form_id(dummy_client, context, response_factory):
    """Test that create validation works when formKey is missing but formId is present."""
    ep = records.RecordsEndpoint(dummy_client, context)
    schema = SchemaCache()
    # Setup schema: Form ID 1 -> Key "F1", Variable "age" in "F1"
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    schema._form_variables = {"F1": {"age": var}}
    schema._form_id_to_key = {1: "F1"}

    dummy_client.post.return_value = response_factory({"jobId": "1"})

    # Case 1: formId is valid, data is invalid (should raise ValidationError)
    # We omit formKey so it falls back to formId
    with pytest.raises(ValidationError):
         ep.create("S1", [{"formId": 1, "data": {"age": "not-an-int"}}], schema=schema)

    dummy_client.post.assert_not_called()

    # Case 2: formId is valid, data is valid
    ep.create("S1", [{"formId": 1, "data": {"age": 25}}], schema=schema)
    dummy_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_async_create_validates_data(dummy_client, context, response_factory):
    """Test that async_create performs validation when schema is provided."""
    # Setup async client mock
    # We need client.post to be an AsyncMock so inspect.iscoroutinefunction returns True
    dummy_client.post = AsyncMock(return_value=response_factory({"jobId": "1"}))

    ep = records.RecordsEndpoint(dummy_client, context)

    # Verify that the endpoint detects it as async client (via _create_impl check)
    # _require_async_client checks self._async_client but here we are passing client to _create_impl indirectly
    # Wait, async_create uses self._async_client.
    # So we need to ensure ep._async_client is set or we mock it.
    # RecordsEndpoint inherits from ListGetEndpoint -> BaseEndpoint.
    # BaseEndpoint initializes with client. If client is async, it sets _async_client.
    # But here dummy_client is a MagicMock (sync).

    # We need to properly initialize RecordsEndpoint with an async client for async_create to work
    # because async_create calls self._require_async_client().

    # Let's mock _async_client on the endpoint
    ep._async_client = dummy_client

    schema = SchemaCache()
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    schema._form_variables = {"F1": {"age": var}}
    schema._form_id_to_key = {1: "F1"}

    # Case 1: Invalid data should raise ValidationError
    with pytest.raises(ValidationError):
        await ep.async_create("S1", [{"formKey": "F1", "data": {"age": "bad"}}], schema=schema)

    dummy_client.post.assert_not_called()

    # Case 2: Valid data
    await ep.async_create("S1", [{"formKey": "F1", "data": {"age": 25}}], schema=schema)
    dummy_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_async_create_validates_using_form_id(dummy_client, context, response_factory):
    """Test that async_create validation works when formKey is missing but formId is present."""
    # Setup async client mock
    dummy_client.post = AsyncMock(return_value=response_factory({"jobId": "1"}))

    ep = records.RecordsEndpoint(dummy_client, context)
    ep._async_client = dummy_client

    schema = SchemaCache()
    # Setup schema: Form ID 1 -> Key "F1", Variable "age" in "F1"
    var = Variable(variable_name="age", variable_type="integer", form_id=1, form_key="F1")
    schema._form_variables = {"F1": {"age": var}}
    schema._form_id_to_key = {1: "F1"}

    # Case 1: formId is valid, data is invalid (should raise ValidationError)
    # We omit formKey so it falls back to formId
    with pytest.raises(ValidationError):
         await ep.async_create("S1", [{"formId": 1, "data": {"age": "not-an-int"}}], schema=schema)

    dummy_client.post.assert_not_called()

    # Case 2: formId is valid, data is valid
    await ep.async_create("S1", [{"formId": 1, "data": {"age": 25}}], schema=schema)
    dummy_client.post.assert_called_once()
