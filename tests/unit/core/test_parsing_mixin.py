"""Test Parsing Mixin module."""

from unittest.mock import MagicMock

from imednet.core.context import Context
from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    """Test suite for MockModel."""

    id: int


class EndpointWithParsing(GenericListGetEndpoint[MockModel]):
    """Test suite for EndpointWithParsing."""

    PATH = "items"
    MODEL = MockModel

    def _auto_filter(self, filters):
        """Test the auto filter functionality."""
        return filters


def test_parsing_mixin_parse_item():
    """Test the test parsing mixin parse item functionality."""
    endpoint = EndpointWithParsing(client=MagicMock(), ctx=Context())
    result = endpoint._parse_item({"id": 1})
    assert isinstance(result, MockModel)
    assert result.id == 1
