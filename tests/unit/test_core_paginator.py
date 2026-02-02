from typing import Any, Dict, List, cast

from imednet.core.paginator import Paginator
from imednet.core.protocols import RequestorProtocol


class DummyClient:
    def __init__(self, responses: List[Dict[str, Any]]):
        self.responses = responses
        self.calls: List[Dict[str, Any]] = []

    def get(self, path: str, params: Dict[str, Any] | None = None):
        self.calls.append({"path": path, "params": params})
        data = self.responses.pop(0)
        return type("Resp", (), {"json": lambda self: data})()


def test_single_page_iteration() -> None:
    client = DummyClient([{"data": [1, 2]}])
    paginator = Paginator(cast(RequestorProtocol, client), "/p")
    assert list(paginator) == [1, 2]
    assert client.calls[0]["params"]["page"] == 0


def test_multiple_page_iteration() -> None:
    client = DummyClient(
        [
            {"data": [1], "pagination": {"totalPages": 2}},
            {"data": [2], "pagination": {"totalPages": 2}},
        ]
    )
    paginator = Paginator(cast(RequestorProtocol, client), "/p", params={"a": 1}, page_size=10)
    items = list(paginator)
    assert items == [1, 2]
    assert client.calls[0]["params"] == {"a": 1, "page": 0, "size": 10}
    assert client.calls[1]["params"] == {"a": 1, "page": 1, "size": 10}
