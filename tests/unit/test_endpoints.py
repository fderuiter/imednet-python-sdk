import httpx
import pytest
from imednet.core.context import Context
from imednet.endpoints.studies import StudiesEndpoint


class DummyClient:
    def __init__(self, response_data):
        self.response_data = response_data
        self.last_path = None

    def get(self, path, params=None):
        self.last_path = path
        return httpx.Response(200, json={"data": self.response_data})


class DummyPaginator:
    def __init__(self, *_args, **_kwargs):
        self.items = [{"studyKey": "S1"}, {"studyKey": "S2"}]

    def __iter__(self):
        return iter(self.items)


def test_studies_list(monkeypatch):
    ctx = Context()
    client = DummyClient([])

    monkeypatch.setattr("imednet.endpoints.studies.Paginator", DummyPaginator)
    ep = StudiesEndpoint(client, ctx)
    studies = ep.list()
    assert [s.study_key for s in studies] == ["S1", "S2"]


def test_studies_get_success():
    ctx = Context()
    client = DummyClient([{"studyKey": "ABC"}])
    ep = StudiesEndpoint(client, ctx)
    study = ep.get("ABC")
    assert study.study_key == "ABC"
    assert client.last_path.endswith("/ABC")


def test_studies_get_missing():
    ctx = Context()
    client = DummyClient([])
    ep = StudiesEndpoint(client, ctx)
    with pytest.raises(ValueError):
        ep.get("MISSING")
