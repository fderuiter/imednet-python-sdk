import pytest
from pydantic import BaseModel
from imednet.core.parsing import get_model_parser, ModelParser

class SimpleModel(BaseModel):
    name: str

class CustomModel(BaseModel):
    name: str

    @classmethod
    def from_json(cls, data):
        return cls(name=data.get("name", "").upper())

def test_get_model_parser_simple():
    parser = get_model_parser(SimpleModel)
    model = parser({"name": "test"})
    assert isinstance(model, SimpleModel)
    assert model.name == "test"

def test_get_model_parser_custom():
    parser = get_model_parser(CustomModel)
    model = parser({"name": "test"})
    assert isinstance(model, CustomModel)
    assert model.name == "TEST"

def test_model_parser_class_simple():
    parser = ModelParser(SimpleModel)
    model = parser.parse({"name": "test"})
    assert isinstance(model, SimpleModel)
    assert model.name == "test"

def test_model_parser_class_many():
    parser = ModelParser(SimpleModel)
    models = parser.parse_many([{"name": "test1"}, {"name": "test2"}])
    assert len(models) == 2
    assert models[0].name == "test1"
    assert models[1].name == "test2"
