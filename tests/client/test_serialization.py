"""Tests for client serialization and deserialization logic."""

import json as py_json
from typing import List

import pytest
import respx
from httpx import Response
from pydantic import ValidationError as PydanticValidationError

from .conftest import BASE_URL, SimpleTestModel


@respx.mock
def test_get_deserialization_single_object(default_client):
    """Test successful GET request deserialization into a single Pydantic model."""
    endpoint = "/items/1"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_data = {"id": 1, "name": "Test Item", "isActive": True}
    mock_route = respx.get(expected_url).mock(return_value=Response(200, json=mock_data))

    # Request with response_model specified
    result = default_client._get(endpoint, response_model=SimpleTestModel)

    assert mock_route.called
    assert isinstance(result, SimpleTestModel)
    assert result.id == mock_data["id"]
    assert result.name == mock_data["name"]
    assert result.is_active == mock_data["isActive"]
    assert result.description is None


@respx.mock
def test_get_deserialization_list_object(default_client):
    """Test successful GET request deserialization into a list of Pydantic models."""
    endpoint = "/items"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_data = [
        {"id": 1, "name": "Item 1", "isActive": True},
        {"id": 2, "name": "Item 2", "description": "Second", "isActive": False},
    ]
    mock_route = respx.get(expected_url).mock(return_value=Response(200, json=mock_data))

    # Request with List[response_model] specified
    result = default_client._get(endpoint, response_model=List[SimpleTestModel])

    assert mock_route.called
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, SimpleTestModel) for item in result)
    assert result[0].id == 1
    assert result[0].name == "Item 1"
    assert result[0].is_active is True
    assert result[1].id == 2
    assert result[1].name == "Item 2"
    assert result[1].description == "Second"
    assert result[1].is_active is False


@respx.mock
def test_get_deserialization_invalid_json(default_client):
    """Test error handling when GET response is not valid JSON."""
    endpoint = "/invalid-json"
    expected_url = f"{BASE_URL}{endpoint}"
    mock_route = respx.get(expected_url).mock(return_value=Response(200, text="not json"))

    with pytest.raises(RuntimeError, match="Failed to decode JSON response"):
        default_client._get(endpoint, response_model=SimpleTestModel)

    assert mock_route.called


@respx.mock
def test_get_deserialization_validation_error(default_client):
    """Test error handling when GET response JSON doesn't match the model."""
    endpoint = "/validation-error"
    expected_url = f"{BASE_URL}{endpoint}"
    # Missing required 'isActive' field
    mock_data = {"id": 1, "name": "Test Item"}
    mock_route = respx.get(expected_url).mock(return_value=Response(200, json=mock_data))

    with pytest.raises(RuntimeError, match="Failed to validate response data") as exc_info:
        default_client._get(endpoint, response_model=SimpleTestModel)

    assert mock_route.called
    # Check that the underlying cause was a Pydantic ValidationError
    assert isinstance(exc_info.value.__cause__, PydanticValidationError)


@respx.mock
def test_post_serialization(default_client):
    """Test successful POST request serialization of a Pydantic model."""
    endpoint = "/items"
    expected_url = f"{BASE_URL}{endpoint}"
    # Create a Pydantic model instance
    payload_model = SimpleTestModel(id=3, name="New Item", isActive=True)
    # Expected JSON string based on model_dump(by_alias=True, mode='json')
    expected_json_payload = {"id": 3, "name": "New Item", "description": None, "isActive": True}

    mock_route = respx.post(expected_url).mock(
        return_value=Response(201, json=payload_model.model_dump(by_alias=True))
    )

    # Pass the model instance directly to the json parameter
    response = default_client._post(endpoint, json=payload_model)

    assert mock_route.called
    request = mock_route.calls.last.request
    # Verify the request content matches the serialized model
    assert py_json.loads(request.content) == expected_json_payload
    assert response.status_code == 201


@respx.mock
def test_post_serialization_and_deserialization(default_client):
    """Test POST request with both Pydantic serialization and deserialization."""
    endpoint = "/items-echo"
    expected_url = f"{BASE_URL}{endpoint}"
    request_model = SimpleTestModel(id=4, name="Echo Item", isActive=False, description="Req")
    response_mock_data = {"id": 4, "name": "Echo Item", "isActive": False, "description": "Resp"}

    mock_route = respx.post(expected_url).mock(return_value=Response(200, json=response_mock_data))

    # Pass request model, expect response model
    result = default_client._post(endpoint, json=request_model, response_model=SimpleTestModel)

    assert mock_route.called
    request = mock_route.calls.last.request
    # Check request serialization
    assert py_json.loads(request.content) == request_model.model_dump(by_alias=True, mode="json")

    # Check response deserialization
    assert isinstance(result, SimpleTestModel)
    assert result.id == response_mock_data["id"]
    assert result.name == response_mock_data["name"]
    assert result.is_active == response_mock_data["isActive"]
    assert result.description == response_mock_data["description"]
