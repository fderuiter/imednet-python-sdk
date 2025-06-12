import os

import httpx
from imednet.core.client import Client
from imednet.metrics import API_CALLS, API_LATENCY, enable_metrics


def test_metrics_incremented() -> None:
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)
    enable_metrics(port=8001)

    client = Client(api_key="a", security_key="b", base_url="https://testserver")
    client._client._transport = httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    before = API_CALLS.labels(method="GET", endpoint="/foo")._value.get()
    client.get("/foo")
    after = API_CALLS.labels(method="GET", endpoint="/foo")._value.get()
    assert after == before + 1
    assert API_LATENCY.labels(method="GET", endpoint="/foo")._sum.get() > 0
