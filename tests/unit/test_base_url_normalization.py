from unittest.mock import MagicMock

import pytest

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    pass


class MockEndpoint(EdcEndpointMixin, GenericEndpoint[MockModel]):
    MODEL = MockModel
    PATH = "/test"


def test_client_strips_api_suffix() -> None:
    client = Client(api_key="k", security_key="s", base_url="https://x/api")
    assert client.base_url == "https://x"


@pytest.mark.asyncio
async def test_async_client_strips_api_suffix() -> None:
    async with AsyncClient(
        api_key="k",
        security_key="s",
        base_url="https://x/api",
    ) as client:
        assert client.base_url == "https://x"


def test_build_safe_path_handles_special_characters() -> None:
    client = MagicMock(spec=Client)
    endpoint = MockEndpoint(client)

    path = endpoint._build_path("user@domain.com", "user%40domain.com")

    assert path == "/api/v1/edc/studies/user@domain.com/user@domain.com"
    assert "%2540" not in path


def test_build_safe_path_prevents_double_slashes() -> None:
    client = MagicMock(spec=Client)
    endpoint = MockEndpoint(client)

    path = endpoint._build_path("//study//", "/subjects/", "///record///")

    assert path == "/api/v1/edc/studies/study/subjects/record"
    assert "//" not in path
