from unittest.mock import MagicMock

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.endpoint.base import BaseEndpoint


def test_build_path_security():
    client = MagicMock(spec=Client)
    ctx = Context()
    endpoint = BaseEndpoint(client, ctx)
    endpoint.BASE_PATH = "api/v1/edc/studies"

    # Case 1: Path Traversal
    # We pass a segment that attempts traversal "../users"
    traversal_input = "../users"

    path = endpoint._build_path(traversal_input, "subjects")

    # Verify that the path does NOT contain unencoded traversal
    # It should effectively encode the slash, making it a single path segment
    assert "/../" not in path
    # And it should contain the encoded version
    assert "..%2Fusers" in path or "%2E%2E%2Fusers" in path

    # Case 2: Query Injection
    injection_input = "my_study?role=admin"
    path_injection = endpoint._build_path(injection_input, "subjects")

    # Verify that the query parameter '?' is encoded
    assert "?" not in path_injection
    assert "%3F" in path_injection
