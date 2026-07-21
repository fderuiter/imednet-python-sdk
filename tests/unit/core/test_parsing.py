"""Unit tests for parsing."""

from typing import Any

from pydantic import BaseModel

from imednet.core.parsing import ModelParser, get_model_parser


class BasicModel(BaseModel):
    """Test suite for BasicModel."""

    id: int
    name: str


class CustomModel(BaseModel):
    """Test suite for CustomModel."""

    id: int
    name: str

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "CustomModel":
        """Helper function to from json."""
        return cls(id=data["id"], name=data["name"] + " (parsed)")


def test_get_model_parser_pydantic_fallback():
    """Test that get model parser pydantic fallback."""
    parser = get_model_parser(BasicModel)
    data = {"id": 1, "name": "Test"}
    model = parser(data)
    assert isinstance(model, BasicModel)
    assert model.id == 1
    assert model.name == "Test"


def test_get_model_parser_custom_method():
    """Test that get model parser custom method."""
    parser = get_model_parser(CustomModel)
    data = {"id": 1, "name": "Test"}
    model = parser(data)
    assert isinstance(model, CustomModel)
    assert model.id == 1
    assert model.name == "Test (parsed)"


def test_model_parser_parse():
    """Test that model parser parse."""
    parser = ModelParser(BasicModel)
    data = {"id": 1, "name": "Test"}
    model = parser.parse(data)
    assert isinstance(model, BasicModel)
    assert model.id == 1
    assert model.name == "Test"


def test_model_parser_parse_many():
    """Test that model parser parse many."""
    parser = ModelParser(CustomModel)
    data = [{"id": 1, "name": "Test1"}, {"id": 2, "name": "Test2"}]
    models = parser.parse_many(data)
    assert len(models) == 2
    assert models[0].id == 1
    assert models[0].name == "Test1 (parsed)"
    assert models[1].id == 2
    assert models[1].name == "Test2 (parsed)"
