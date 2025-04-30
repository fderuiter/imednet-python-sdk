from unittest.mock import Mock

import pytest
from imednet.endpoints.base import BaseEndpoint


class DummyEndpoint(BaseEndpoint):
    path = "/api/v1/test"


def test_auto_filter_injects_study_key():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = "ABC123"
    endpoint = DummyEndpoint(client, ctx)
    filters = {}
    result = endpoint._auto_filter(filters)
    assert result["studyKey"] == "ABC123"


def test_auto_filter_preserves_existing_study_key():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = "ABC123"
    endpoint = DummyEndpoint(client, ctx)
    filters = {"studyKey": "DEF456"}
    result = endpoint._auto_filter(filters)
    assert result["studyKey"] == "DEF456"


def test_auto_filter_no_default_study_key():
    client = Mock()
    ctx = Mock()
    ctx.default_study_key = None
    endpoint = DummyEndpoint(client, ctx)
    filters = {}
    result = endpoint._auto_filter(filters)
    assert "studyKey" not in result


@pytest.mark.parametrize(
    "args,expected",
    [
        ((), "/api/v1/test"),
        (("foo",), "/api/v1/test/foo"),
        (("foo", "bar"), "/api/v1/test/foo/bar"),
        (("foo/", "/bar/"), "/api/v1/test/foo/bar"),
    ],
)
def test_build_path(args, expected):
    client = Mock()
    ctx = Mock()
    endpoint = DummyEndpoint(client, ctx)
    assert endpoint._build_path(*args) == expected
