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


def test_endpoint_abc_validate_study_key_raises():
    from imednet.errors import ClientError

    endpoint = ConcreteEndpoint()
    with pytest.raises(ClientError, match="Study key must be provided"):
        endpoint._validate_study_key(None)


def test_endpoint_abc_validate_study_key_passes():
    endpoint = ConcreteEndpoint()
    endpoint._validate_study_key("STUDY123")  # Should not raise


def test_endpoint_abc_get_endpoint_path():
    endpoint = ConcreteEndpoint()
    path = endpoint._get_endpoint_path("STUDY123", "extra", 1)
    assert path == "mock/STUDY123/mock/extra/1"


def test_endpoint_abc_raise_not_found():
    from imednet.errors import NotFoundError

    endpoint = ConcreteEndpoint()
    with pytest.raises(NotFoundError, match="MockModel 1 not found in study STUDY123"):
        endpoint._raise_not_found("STUDY123", 1)


def test_endpoint_abc_raise_not_found_no_id():
    from imednet.errors import NotFoundError

    endpoint = ConcreteEndpoint()
    with pytest.raises(NotFoundError, match="MockModel not found in study STUDY123"):
        endpoint._raise_not_found("STUDY123")


def test_endpoint_abc_raise_not_found_no_study():
    from imednet.errors import NotFoundError

    endpoint = ConcreteEndpoint()
    endpoint.requires_study_key = False
    with pytest.raises(NotFoundError, match="MockModel 1 not found"):
        endpoint._raise_not_found(None, 1)
