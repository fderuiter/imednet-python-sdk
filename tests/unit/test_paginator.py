import httpx
from imednet.core.paginator import Paginator


class DummyClient:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    def get(self, path, params=None):
        call_num = len(self.calls)
        self.calls.append((path, params))
        return self._responses[call_num]


def make_response(items, total_pages):
    return httpx.Response(200, json={'data': items, 'pagination': {'totalPages': total_pages}})


def test_paginator_iterates_through_pages():
    responses = [
        make_response([1, 2], 2),
        make_response([3], 2),
    ]
    client = DummyClient(responses)
    paginator = Paginator(client, '/items', page_size=2)
    assert list(paginator) == [1, 2, 3]
    assert client.calls[0][1]['page'] == 0
    assert client.calls[1][1]['page'] == 1
