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

# Map types to their default normalizers
_TYPE_VALIDATORS: Dict[Any, Callable[[Any], Any]] = {
    str: parse_str_or_default,
    int: parse_int_or_default,
    bool: parse_bool,
    datetime: parse_datetime,
    # Container types based on origin
    list: parse_list_or_default,
    dict: parse_dict_or_default,
}


def _identity(v: Any) -> Any:
    return v


def _make_optional_normalizer(
    validator: Callable[[Any], Any], annotation: Any
) -> Callable[[Any], Any]:
    """Create a wrapper that preserves None for optional fields."""
    if annotation is datetime:
        # For datetime, we want None if the value is empty/None,
        # instead of the sentinel value returned by parse_datetime.
        return lambda v: None if not v else validator(v)

    # For other primitives, we only want to return None if the input is explicitly None.
    # Otherwise we run the validator (which typically handles None by returning a default,
    # but here we intercept None first).
    return lambda v: None if v is None else validator(v)


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

    # Check if we have a direct validator for the origin (list, dict) or the annotation (str, int, etc)
    key = origin if origin in _TYPE_VALIDATORS else annotation
    normalizer = _TYPE_VALIDATORS.get(key, _identity)

    if optional and normalizer is not _identity:
        # Container types (list, dict) in the original code did NOT have optional logic applied
        # (they default to empty list/dict via parse_list/dict_or_default even if optional).
        # Only primitives (str, int, bool, datetime) had optional logic.
        if key in (str, int, bool, datetime):
            normalizer = _make_optional_normalizer(normalizer, key)

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
