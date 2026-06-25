"""Tests for test_security_path_traversal."""

from unittest.mock import MagicMock

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.endpoint.base import GenericEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    """Test suite for MockModel."""

    pass


class MockEndpoint(EdcEndpointMixin, GenericEndpoint[MockModel]):
    """Test suite for MockEndpoint."""

    MODEL = MockModel
    PATH = "/test"


def test_build_path_security():
    """Test test_build_path_security behavior."""
    client = MagicMock(spec=Client)
    ctx = Context()
    endpoint = MockEndpoint(client, ctx)
    endpoint.BASE_PATH = "api/v1/edc/studies"

    # Case 1: Path Traversal
    # We pass a segment that attempts traversal "../users"
    traversal_input = "../users"

    path = endpoint._build_path(traversal_input, "subjects")

    # build_safe_path uses httpx URL resolution which normalises .. segments,
    # so no raw "/../" sequence or residual ".." component appears in the result.
    assert "/../" not in path
    assert ".." not in path

    # Case 2: Query Injection
    injection_input = "my_study?role=admin"
    path_injection = endpoint._build_path(injection_input, "subjects")

    # httpx treats "?" as the query-string boundary; the path portion never
    # contains "?" or the injected query content.
    assert "?" not in path_injection
    assert "role=admin" not in path_injection
