"""TODO: Add docstring."""

from typing import Any, Dict

from pydantic import BaseModel

from imednet.core.parsing import ModelParser, get_model_parser


class BasicModel(BaseModel):
    """TODO: Add docstring."""

    id: int
    name: str


class CustomModel(BaseModel):
    """TODO: Add docstring."""

    id: int
    name: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "CustomModel":
        """TODO: Add docstring."""
        return cls(id=data["id"], name=data["name"] + " (parsed)")


def test_get_model_parser_pydantic_fallback():
    """TODO: Add docstring."""
    parser = get_model_parser(BasicModel)
    data = {"id": 1, "name": "Test"}
    model = parser(data)
    assert isinstance(model, BasicModel)
    assert model.id == 1
    assert model.name == "Test"


def test_get_model_parser_custom_method():
    """TODO: Add docstring."""
    parser = get_model_parser(CustomModel)
    data = {"id": 1, "name": "Test"}
    model = parser(data)
    assert isinstance(model, CustomModel)
    assert model.id == 1
    assert model.name == "Test (parsed)"


def test_model_parser_parse():
    """TODO: Add docstring."""
    parser = ModelParser(BasicModel)
    data = {"id": 1, "name": "Test"}
    model = parser.parse(data)
    assert isinstance(model, BasicModel)
    assert model.id == 1
    assert model.name == "Test"


def test_model_parser_parse_many():
    """TODO: Add docstring."""
    parser = ModelParser(CustomModel)
    data = [{"id": 1, "name": "Test1"}, {"id": 2, "name": "Test2"}]
    models = parser.parse_many(data)
    assert len(models) == 2
    assert models[0].id == 1
    assert models[0].name == "Test1 (parsed)"
    assert models[1].id == 2
    assert models[1].name == "Test2 (parsed)"
