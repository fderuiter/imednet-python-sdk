import pytest
from imednet.core.paginator import Paginator

class DummyClient:
    def __init__(self, response_data):
        self.response_data = response_data

    def get(self, path, params=None):
        data = self.response_data
        return type("Resp", (), {"json": lambda self: data})()

def test_paginator_raises_on_non_list_data():
    """Test that Paginator raises TypeError if data field is not a list."""
    # This prevents subtle bugs where iterating over a string yields characters
    client = DummyClient({"data": "invalid_string_not_list"})
    paginator = Paginator(client, "/p")

    with pytest.raises(TypeError, match="Expected list for key 'data'"):
        list(paginator)

def test_paginator_raises_on_non_dict_response():
    """Test that Paginator raises TypeError if response payload is not a dict."""
    # BasePaginator expects a dict response (containing data and pagination keys)
    client = DummyClient(["not", "a", "dict"])
    paginator = Paginator(client, "/p")

    with pytest.raises(TypeError, match="Expected JSON object"):
        list(paginator)
