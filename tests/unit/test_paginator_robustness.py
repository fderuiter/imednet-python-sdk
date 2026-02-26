from unittest.mock import Mock

import pytest

from imednet.core.paginator import Paginator


class MockClient:
    def __init__(self, response_data):
        self.response_data = response_data

    def get(self, path, params=None):
        response = Mock()
        response.json.return_value = self.response_data
        return response


def test_paginator_raises_type_error_on_list_response():
    """
    Test that the Paginator raises a helpful TypeError when the API returns a list
    instead of the expected dictionary structure.
    """
    client = MockClient(["item1", "item2"])
    paginator = Paginator(client, "/path")

    with pytest.raises(TypeError, match="API response must be a dictionary"):
        list(paginator)


def test_paginator_raises_type_error_on_scalar_response():
    """
    Test that the Paginator raises a helpful TypeError when the API returns a scalar
    (e.g. string) instead of the expected dictionary structure.
    """
    client = MockClient("unexpected string")
    paginator = Paginator(client, "/path")

    with pytest.raises(TypeError, match="API response must be a dictionary"):
        list(paginator)


def test_paginator_raises_type_error_on_invalid_data_key():
    """
    Test that the Paginator raises a helpful TypeError when the data key in the response
    is not a list.
    """
    # unexpected: 'data' is a dict, not a list
    client = MockClient({"data": {"key": "value"}})
    paginator = Paginator(client, "/path")

    with pytest.raises(TypeError, match="Expected a list of items"):
        list(paginator)


def test_paginator_raises_type_error_on_invalid_pagination_field():
    """
    Test that the Paginator raises a helpful TypeError when the pagination key in the response
    is not a dictionary.
    """
    # unexpected: 'pagination' is a string, not a dict
    client = MockClient({
        "data": [{"id": 1}],
        "pagination": "invalid_structure"
    })
    paginator = Paginator(client, "/path")

    # Before the fix, this raises AttributeError because it tries to call .get() on a string
    with pytest.raises(TypeError, match="Response field 'pagination' must be a dictionary"):
        list(paginator)
