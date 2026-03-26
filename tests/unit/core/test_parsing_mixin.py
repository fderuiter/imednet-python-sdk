from imednet.core.endpoint.mixins.parsing import ParsingMixin
from imednet.models.json_base import JsonModel


class MockModel(JsonModel):
    id: int


class EndpointWithParsing(ParsingMixin[MockModel]):
    MODEL = MockModel


def test_parsing_mixin_parse_item():
    endpoint = EndpointWithParsing()
    result = endpoint._parse_item({"id": 1})
    assert isinstance(result, MockModel)
    assert result.id == 1
