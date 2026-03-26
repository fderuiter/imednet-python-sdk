from typing import Any, Dict, Type

import pytest

from imednet.core.endpoint.abc import EndpointABC
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    id: int


class ConcreteEndpoint(EndpointABC[MockModel]):
    @property
    def PATH(self) -> str:  # noqa: N802
        return "mock"

    @property
    def MODEL(self) -> Type[MockModel]:  # noqa: N802
        return MockModel

    def _build_path(self, *segments: Any) -> str:
        return "/".join(["mock", *(str(s) for s in segments)])

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        return {"auto": True, **filters}


class UnimplementedEndpoint(EndpointABC[MockModel]):
    pass


def test_endpoint_abc_properties():
    endpoint = ConcreteEndpoint()
    assert endpoint.PATH == "mock"
    assert endpoint.MODEL == MockModel
    assert endpoint.requires_study_key is True
    assert endpoint._id_param == "id"
    assert endpoint._enable_cache is False


def test_endpoint_abc_methods():
    endpoint = ConcreteEndpoint()
    assert endpoint._build_path(1, "test") == "mock/1/test"
    assert endpoint._auto_filter({"test": "value"}) == {"auto": True, "test": "value"}


def test_endpoint_abc_abstract_instantiation_fails():
    with pytest.raises(TypeError) as exc_info:
        UnimplementedEndpoint()  # type: ignore[abstract]
    assert "Can't instantiate abstract class" in str(exc_info.value)


def test_endpoint_abc_pass_coverage():
    # Hit the `pass` statements in abstract properties/methods to ensure 100% coverage
    assert EndpointABC.PATH.fget(None) is None
    assert EndpointABC.MODEL.fget(None) is None
    assert EndpointABC._build_path(None) is None
    assert EndpointABC._auto_filter(None, {}) is None
