from __future__ import annotations

from typing import Any, List, Optional

import httpx
import pytest
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.endpoints.studies import StudiesEndpoint


class DummyClient(Client):
    def __init__(self, response_data: List[dict[str, str]]) -> None:
        super().__init__("k", "s", base_url="http://test")
        self.response_data = response_data
        self.last_path: Optional[str] = None

    def get(
        self, path: str, params: Optional[dict[str, Any]] = None, **kwargs: Any
    ) -> httpx.Response:
        self.last_path = path
        return httpx.Response(200, json={"data": self.response_data})


class DummyPaginator:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self.items: List[dict[str, str]] = [{"studyKey": "S1"}, {"studyKey": "S2"}]

    def __iter__(self):
        return iter(self.items)


def test_studies_list(monkeypatch: pytest.MonkeyPatch) -> None:
    ctx = Context()
    client = DummyClient([])

    monkeypatch.setattr("imednet.endpoints.studies.Paginator", DummyPaginator)
    ep = StudiesEndpoint(client, ctx)
    studies = ep.list()
    assert [s.study_key for s in studies] == ["S1", "S2"]


def test_studies_get_success() -> None:
    ctx = Context()
    client = DummyClient([{"studyKey": "ABC"}])
    ep = StudiesEndpoint(client, ctx)
    study = ep.get("ABC")
    assert study.study_key == "ABC"
    assert client.last_path.endswith("/ABC")


def test_studies_get_missing() -> None:
    ctx = Context()
    client = DummyClient([])
    ep = StudiesEndpoint(client, ctx)
    with pytest.raises(ValueError):
        ep.get("MISSING")
