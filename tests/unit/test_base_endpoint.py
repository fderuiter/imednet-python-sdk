from __future__ import annotations

from imednet.core.context import Context
from imednet.endpoints.base import BaseEndpoint


class DummyEndpoint(BaseEndpoint):
    path = "studies"


def test_build_path() -> None:
    ctx = Context()
    ep = DummyEndpoint(client=None, ctx=ctx)
    assert ep._build_path("123") == "/studies/123"
    assert ep._build_path("/123/") == "/studies/123"


def test_auto_filter_injects_default() -> None:
    ctx = Context()
    ctx.set_default_study_key("DEF")
    ep = DummyEndpoint(client=None, ctx=ctx)
    result = ep._auto_filter({"foo": 1})
    assert result == {"foo": 1, "studyKey": "DEF"}


def test_auto_filter_respects_existing() -> None:
    ctx = Context()
    ctx.set_default_study_key("DEF")
    ep = DummyEndpoint(client=None, ctx=ctx)
    result = ep._auto_filter({"studyKey": "ABC"})
    assert result == {"studyKey": "ABC"}
