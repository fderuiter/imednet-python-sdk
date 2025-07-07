import httpx
from imednet.core.client import Client
from imednet.core.exceptions import ServerError
from imednet.core.retry import DefaultRetryPolicy, RetryState


def test_default_policy_request_error():
    policy = DefaultRetryPolicy()
    state = RetryState(
        1, exception=httpx.RequestError("boom", request=httpx.Request("GET", "https://x"))
    )
    assert policy.should_retry(state)
    assert not policy.should_retry(RetryState(1))


def test_custom_policy(monkeypatch):
    class ServerPolicy:
        def should_retry(self, state: RetryState) -> bool:
            return isinstance(state.exception, ServerError)

    client = Client("k", "s", base_url="https://api.test", retries=3, retry_policy=ServerPolicy())
    calls = {"count": 0}

    def request(method: str, url: str, **kwargs: object) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] < 3:
            raise ServerError({}, status_code=500)
        return httpx.Response(200, json={"ok": True})

    monkeypatch.setattr(client._executor, "send", request)

    resp = client.get("/x")

    assert resp.status_code == 200
    assert calls["count"] == 3
