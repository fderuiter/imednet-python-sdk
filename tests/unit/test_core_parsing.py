"""TODO: Add docstring."""
from typing import Any

from pydantic import BaseModel

from imednet.core.parsing import ModelParser, get_model_parser


class SimpleModel(BaseModel):
    """TODO: Add docstring."""
    id: int
    name: str


class CustomParseModel(BaseModel):
    """TODO: Add docstring."""
    id: int
    name: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "CustomParseModel":
        """TODO: Add docstring."""
        return cls(id=data["identifier"], name=data["full_name"])


def test_get_model_parser_uses_model_validate_by_default() -> None:
    """TODO: Add docstring."""
    parser = get_model_parser(SimpleModel)
    assert parser == SimpleModel.model_validate

    data = {"id": 1, "name": "Test"}
    instance = parser(data)
    assert isinstance(instance, SimpleModel)
    assert instance.id == 1
    assert instance.name == "Test"


def test_get_model_parser_uses_custom_from_json() -> None:
    """TODO: Add docstring."""
    parser = get_model_parser(CustomParseModel)
    assert parser == CustomParseModel.from_json

    data = {"identifier": 2, "full_name": "Custom"}
    instance = parser(data)
    assert isinstance(instance, CustomParseModel)
    assert instance.id == 2
    assert instance.name == "Custom"


def test_model_parser_class_parse() -> None:
    """TODO: Add docstring."""
    parser = ModelParser(SimpleModel)
    data = {"id": 3, "name": "Class Test"}

    instance = parser.parse(data)
    assert isinstance(instance, SimpleModel)
    assert instance.id == 3
    assert instance.name == "Class Test"


def test_model_parser_class_parse_many() -> None:
    """TODO: Add docstring."""
    parser = ModelParser(CustomParseModel)
    data_list = [
        {"identifier": 10, "full_name": "Alice"},
        {"identifier": 20, "full_name": "Bob"},
    ]

    instances = parser.parse_many(data_list)
    assert len(instances) == 2
    assert isinstance(instances[0], CustomParseModel)
    assert instances[0].id == 10
    assert instances[0].name == "Alice"
    assert instances[1].id == 20
    assert instances[1].name == "Bob"
