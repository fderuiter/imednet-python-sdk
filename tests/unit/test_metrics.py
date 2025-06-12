import imednet.metrics as metrics
from imednet.core.client import Client


class DummyResponse:
    def __init__(self, status: int = 200):
        self.status_code = status
        self.request = None

    def json(self):
        return {}

    @property
    def text(self):
        return ""

    @property
    def is_error(self):
        return self.status_code >= 400


def test_metrics_updated(monkeypatch) -> None:
    client = Client(api_key="A", security_key="B")
    resp = DummyResponse(200)
    monkeypatch.setattr(client._client, "request", lambda *a, **kw: resp)

    before = metrics.API_CALLS.labels(endpoint="/path", method="GET", status="200")._value.get()
    client.get("/path")
    after = metrics.API_CALLS.labels(endpoint="/path", method="GET", status="200")._value.get()

    assert after == before + 1
    assert metrics.API_LATENCY.labels(endpoint="/path", method="GET")._sum.get() > 0
