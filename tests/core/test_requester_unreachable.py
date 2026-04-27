import httpx
import pytest
import respx
from tenacity import RetryError
from imednet.core.http.executor import SyncRequestExecutor
from imednet.core.http.monitor import RequestMonitor

class FakeAttempt:
    def __init__(self, failed):
        self.failed = failed

    def exception(self):
        return RuntimeError("Fake error")

    def result(self):
        return httpx.Response(200, json={"ok": True})

class FakeRetryError(RetryError):
    def __init__(self, failed):
        self.last_attempt = FakeAttempt(failed)
        super().__init__(self.last_attempt)

def test_sync_executor_unreachable_branch(monkeypatch):
    client = httpx.Client(base_url="https://api.test")

    def mock_retryer(*args, **kwargs):
        raise FakeRetryError(False)

    monkeypatch.setattr("tenacity.Retrying.__call__", mock_retryer)

    executor = SyncRequestExecutor(client.request, retries=0, backoff_factor=0)

    resp = executor("GET", "/ping")
    assert resp.status_code == 200

    client.close()
