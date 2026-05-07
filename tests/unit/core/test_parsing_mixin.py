from imednet.core.context import Context
from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.models.json_base import JsonModel
from unittest.mock import MagicMock


class MockModel(JsonModel):
    id: int


class EndpointWithParsing(GenericListGetEndpoint[MockModel]):
    PATH = "items"
    MODEL = MockModel

    def _auto_filter(self, filters):
        return filters


def test_parsing_mixin_parse_item():
    endpoint = EndpointWithParsing(client=MagicMock(), ctx=Context())
    result = endpoint._parse_item({"id": 1})
    assert isinstance(result, MockModel)
    assert result.id == 1
