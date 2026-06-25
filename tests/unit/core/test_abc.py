"""Tests for test_abc."""

from typing import Any, Dict, Type

import pytest

from imednet.core.endpoint.abc import EndpointABC
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    """Test suite for MockModel."""

    id: int


class ConcreteEndpoint(EndpointABC[MockModel]):
    """Test suite for ConcreteEndpoint."""

    @property
    def PATH(self) -> str:  # noqa: N802
        """Test PATH behavior."""
        return "mock"

    @property
    def MODEL(self) -> Type[MockModel]:  # noqa: N802
        """Test MODEL behavior."""
        return MockModel

    def _build_path(self, *segments: Any) -> str:
        """Test _build_path behavior."""
        return "/".join(["mock", *(str(s) for s in segments)])

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Test _auto_filter behavior."""
        return {"auto": True, **filters}


class UnimplementedEndpoint(EndpointABC[MockModel]):
    """Test suite for UnimplementedEndpoint."""

    pass


def test_endpoint_abc_properties():
    """Test test_endpoint_abc_properties behavior."""
    endpoint = ConcreteEndpoint()
    assert endpoint.PATH == "mock"
    assert endpoint.MODEL == MockModel
    assert endpoint.requires_study_key is True
    assert endpoint._id_param == "id"


def test_endpoint_abc_methods():
    """Test test_endpoint_abc_methods behavior."""
    endpoint = ConcreteEndpoint()
    assert endpoint._build_path(1, "test") == "mock/1/test"
    assert endpoint._auto_filter({"test": "value"}) == {"auto": True, "test": "value"}


def test_endpoint_abc_abstract_instantiation_fails():
    """Test test_endpoint_abc_abstract_instantiation_fails behavior."""
    with pytest.raises(TypeError) as exc_info:
        UnimplementedEndpoint()  # type: ignore[abstract]
    assert "Can't instantiate abstract class" in str(exc_info.value)


def test_endpoint_abc_pass_coverage():
    """Test test_endpoint_abc_pass_coverage behavior."""
    # Hit the `pass` statements in abstract properties/methods to ensure 100% coverage
    assert EndpointABC.PATH.fget(None) is None
    assert EndpointABC.MODEL.fget(None) is None
    assert EndpointABC._build_path(None) is None
    assert EndpointABC._auto_filter(None, {}) is None
