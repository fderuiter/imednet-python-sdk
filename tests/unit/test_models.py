from datetime import datetime
from typing import Any, Union, get_args, get_origin

import pytest
from pydantic import BaseModel, ValidationError

import imednet.api.models as models


def _build_value(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin is list:
        sub = get_args(annotation)[0]
        return [_build_value(sub)]
    if origin is dict:
        return {"k": "v"}
    if origin is Union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if not args:
            return None
        sub = args[0]
        if sub is datetime:
            return ""
        return _build_value(sub)
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _build_sample_data(annotation)
    if annotation is int:
        return "1"
    if annotation is bool:
        return "true"
    if annotation is datetime:
        return "2024-01-01T00:00:00Z"
    return "value"


def _build_sample_data(cls: type[BaseModel]) -> Any:
    if getattr(cls, "__pydantic_root_model__", False):
        return {"foo": "bar"}
    data = {}
    for name, field in cls.model_fields.items():
        data[field.alias or name] = _build_value(field.annotation)
    return data


MODEL_CLASSES = [
    cls
    for cls in (v for v in vars(models).values() if isinstance(v, type))
    if issubclass(cls, BaseModel) and cls.__module__.startswith("imednet.api.models")
]


@pytest.mark.parametrize("model_cls", MODEL_CLASSES)
def test_model_instantiation_and_dump(model_cls: type[BaseModel]) -> None:
    sample = _build_sample_data(model_cls)
    model = model_cls.model_validate(sample)
    dumped = model.model_dump(by_alias=True)
    if not getattr(model_cls, "__pydantic_root_model__", False):
        for name, field in model_cls.model_fields.items():
            alias = field.alias or name
            assert alias in dumped
    else:
        assert dumped == sample


@pytest.mark.parametrize("model_cls", MODEL_CLASSES)
def test_missing_required_fields(model_cls: type[BaseModel]) -> None:
    if getattr(model_cls, "__pydantic_root_model__", False):
        model_cls.model_validate({})
        return
    required = [f for f in model_cls.model_fields.values() if f.is_required()]
    if required:
        with pytest.raises(ValidationError):
            model_cls.model_validate({})
    else:
        instance = model_cls.model_validate({})
        assert isinstance(instance, model_cls)


@pytest.mark.parametrize("model_cls", MODEL_CLASSES)
def test_invalid_int_defaults(model_cls: type[BaseModel]) -> None:
    if getattr(model_cls, "__pydantic_root_model__", False):
        pytest.skip("root model")
    int_field_item = next(
        (
            (name, field)
            for name, field in model_cls.model_fields.items()
            if field.annotation is int and not field.is_required()
        ),
        None,
    )
    if not int_field_item:
        pytest.skip("no int field")
    name, field = int_field_item
    data = _build_sample_data(model_cls)
    data[field.alias or name] = "notanint"
    model = model_cls.model_validate(data)
    assert getattr(model, name) == 0
