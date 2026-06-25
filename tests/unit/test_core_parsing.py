"""Unit tests for core parsing."""

from typing import Any

from pydantic import BaseModel

from imednet.core.parsing import ModelParser, get_model_parser


class SimpleModel(BaseModel):
    """Test suite for SimpleModel."""

    id: int
    name: str


class CustomParseModel(BaseModel):
    """Test suite for CustomParseModel."""

    id: int
    name: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "CustomParseModel":
        """Helper function to from json."""
        return cls(id=data["identifier"], name=data["full_name"])


def test_get_model_parser_uses_model_validate_by_default() -> None:
    """Test that get model parser uses model validate by default."""
    parser = get_model_parser(SimpleModel)
    assert parser == SimpleModel.model_validate

    data = {"id": 1, "name": "Test"}
    instance = parser(data)
    assert isinstance(instance, SimpleModel)
    assert instance.id == 1
    assert instance.name == "Test"


def test_get_model_parser_uses_custom_from_json() -> None:
    """Test that get model parser uses custom from json."""
    parser = get_model_parser(CustomParseModel)
    assert parser == CustomParseModel.from_json

    data = {"identifier": 2, "full_name": "Custom"}
    instance = parser(data)
    assert isinstance(instance, CustomParseModel)
    assert instance.id == 2
    assert instance.name == "Custom"


def test_model_parser_class_parse() -> None:
    """Test that model parser class parse."""
    parser = ModelParser(SimpleModel)
    data = {"id": 3, "name": "Class Test"}

    instance = parser.parse(data)
    assert isinstance(instance, SimpleModel)
    assert instance.id == 3
    assert instance.name == "Class Test"


def test_model_parser_class_parse_many() -> None:
    """Test that model parser class parse many."""
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
