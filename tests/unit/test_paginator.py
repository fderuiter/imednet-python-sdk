from __future__ import annotations

from typing import List, Optional

import httpx
from imednet.core.paginator import Paginator


class DummyClient:
    def __init__(self, responses: List[httpx.Response]) -> None:
        self._responses = responses
        self.calls: List[tuple[str, Optional[dict[str, int]]]] = []

    def get(self, path: str, params: Optional[dict[str, int]] = None) -> httpx.Response:
        call_num = len(self.calls)
        self.calls.append((path, params))
        return self._responses[call_num]


def make_response(items: List[int], total_pages: int) -> httpx.Response:
    return httpx.Response(200, json={"data": items, "pagination": {"totalPages": total_pages}})


def test_paginator_iterates_through_pages() -> None:
    responses = [
        make_response([1, 2], 2),
        make_response([3], 2),
    ]
    client = DummyClient(responses)
    paginator = Paginator(client, "/items", page_size=2)
    assert list(paginator) == [1, 2, 3]
    assert client.calls[0][1]["page"] == 0
    assert client.calls[1][1]["page"] == 1
