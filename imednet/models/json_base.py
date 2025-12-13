from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, field_validator
from typing_extensions import Self

from imednet.utils.validators import (
    parse_bool,
    parse_datetime,
    parse_dict_or_default,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)

_NORMALIZERS: Dict[type, Dict[str, Callable[[Any], Any]]] = {}


def _identity(v: Any) -> Any:
    return v


def _get_normalizer(cls: type[BaseModel], field_name: str) -> Callable[[Any], Any]:
    if cls in _NORMALIZERS and field_name in _NORMALIZERS[cls]:
        return _NORMALIZERS[cls][field_name]

    field = cls.model_fields[field_name]
    annotation = field.annotation
    origin = get_origin(annotation)
    optional = False

    if origin is Union:
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            annotation = args[0]
            origin = get_origin(annotation)
            optional = True

    normalizer = _identity

    if origin is list:
        normalizer = parse_list_or_default
    elif origin is dict:
        normalizer = parse_dict_or_default
    elif annotation is str:
        if optional:

            def normalizer(v: Any) -> Any:
                return None if v is None else parse_str_or_default(v)

        else:
            normalizer = parse_str_or_default
    elif annotation is int:
        if optional:

            def normalizer(v: Any) -> Any:
                return None if v is None else parse_int_or_default(v)

        else:
            normalizer = parse_int_or_default
    elif annotation is bool:
        if optional:

            def normalizer(v: Any) -> Any:
                return None if v is None else parse_bool(v)

        else:
            normalizer = parse_bool
    elif annotation is datetime:
        if optional:

            def normalizer(v: Any) -> Any:
                return None if not v else parse_datetime(v)

        else:
            normalizer = parse_datetime

    if cls not in _NORMALIZERS:
        _NORMALIZERS[cls] = {}
    _NORMALIZERS[cls][field_name] = normalizer
    return normalizer


class JsonModel(BaseModel):
    """Base model with shared JSON parsing helpers."""

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def from_json(cls, data: Any) -> Self:
        """Validate data coming from JSON APIs."""
        return cls.model_validate(data)

    @field_validator("*", mode="before")
    def _normalise(cls, v: Any, info: Any) -> Any:  # noqa: D401
        """Normalize common primitive types before validation."""
        if not info.field_name:
            return v

        # Bolt Optimization: Avoid function call overhead in hot path
        try:
            return _NORMALIZERS[cls][info.field_name](v)
        except KeyError:
            return _get_normalizer(cls, info.field_name)(v)
