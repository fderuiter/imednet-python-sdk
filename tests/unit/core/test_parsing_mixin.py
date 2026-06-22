"""TODO: Add docstring."""

from unittest.mock import MagicMock

from imednet.core.context import Context
from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    """TODO: Add docstring."""

    id: int


class EndpointWithParsing(GenericListGetEndpoint[MockModel]):
    """TODO: Add docstring."""

    PATH = "items"
    MODEL = MockModel

    def _auto_filter(self, filters):
        """TODO: Add docstring."""
        return filters


def test_parsing_mixin_parse_item():
    """TODO: Add docstring."""
    endpoint = EndpointWithParsing(client=MagicMock(), ctx=Context())
    result = endpoint._parse_item({"id": 1})
    assert isinstance(result, MockModel)
    assert result.id == 1
