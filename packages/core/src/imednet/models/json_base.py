from __future__ import annotations

import types
from datetime import datetime
from typing import Any, Callable, Dict, Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
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


def _optional_str(v: Any) -> Any:
    return None if v is None else parse_str_or_default(v)


def _optional_int(v: Any) -> Any:
    return None if v is None else parse_int_or_default(v)


def _optional_bool(v: Any) -> Any:
    return None if v is None else parse_bool(v)


def _optional_datetime(v: Any) -> Any:
    return None if not v else parse_datetime(v)


def _optional_dict(v: Any) -> Any:
    return None if v is None else parse_dict_or_default(v)


def _optional_list(v: Any) -> Any:
    return None if v is None else parse_list_or_default(v)


def _extract_single_item(v: Any) -> Any:
    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
        import logging

        logging.getLogger(__name__).warning(
            "Structural shift detected: API returned a list where an object was expected. Coercing by extracting the first item."
        )
        return v[0]
    return v


def _get_normalizer(cls: type[BaseModel], field_name: str) -> Callable[[Any], Any]:
    if cls in _NORMALIZERS and field_name in _NORMALIZERS[cls]:
        return _NORMALIZERS[cls][field_name]

    field = cls.model_fields[field_name]
    annotation = field.annotation
    origin = get_origin(annotation)
    optional = False

    if origin is Union or (hasattr(types, "UnionType") and origin is types.UnionType):
        args = [a for a in get_args(annotation) if a is not type(None)]
        if len(args) == 1:
            annotation = args[0]
            origin = get_origin(annotation)
            optional = True

    normalizer = _identity

    if origin is list:
        normalizer = _optional_list if optional else parse_list_or_default
    elif origin is dict:
        normalizer = _optional_dict if optional else parse_dict_or_default
    elif annotation is str:
        normalizer = _optional_str if optional else parse_str_or_default
    elif annotation is int:
        normalizer = _optional_int if optional else parse_int_or_default
    elif annotation is bool:
        normalizer = _optional_bool if optional else parse_bool
    elif annotation is datetime:
        normalizer = _optional_datetime if optional else parse_datetime
    elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
        normalizer = _extract_single_item

    if cls not in _NORMALIZERS:
        _NORMALIZERS[cls] = {}
    _NORMALIZERS[cls][field_name] = normalizer
    return normalizer


import os


class JsonModel(BaseModel):
    """Base model with shared JSON parsing helpers."""

    model_config = ConfigDict(
        extra="forbid"
        if os.environ.get("IMEDNET_STRICT_MODE", "").lower() in ("1", "true")
        else "ignore",
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    @classmethod
    def from_json(cls, data: Any) -> Self:
        """Validate data coming from JSON APIs."""
        try:
            return cls.model_validate(data)
        except Exception as e:
            import logging

            logging.getLogger("imednet.drift").warning(
                f"Drift detected (destructive): {cls.__name__} validation failed: {e}"
            )
            raise

    @model_validator(mode="before")
    @classmethod
    def _detect_drift(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        import logging

        logger = logging.getLogger("imednet.drift")

        defined_fields = set(cls.model_fields.keys())
        for name, field in cls.model_fields.items():
            if field.alias:
                defined_fields.add(field.alias)
        for name in getattr(cls, "model_computed_fields", {}).keys():
            defined_fields.add(name)

        incoming_keys = set(data.keys())

        unexpected_fields = incoming_keys - defined_fields
        if unexpected_fields:
            logger.warning(
                f"Drift detected (additive): {cls.__name__} received unexpected fields: {', '.join(sorted(unexpected_fields))}"
            )

        missing_fields = []
        for name, field in cls.model_fields.items():
            if field.is_required():
                if name not in incoming_keys and (
                    not field.alias or field.alias not in incoming_keys
                ):
                    missing_fields.append(name)
        if missing_fields:
            logger.warning(
                f"Drift detected (destructive): {cls.__name__} missing required fields: {', '.join(sorted(missing_fields))}"
            )

        return data

    @field_validator("*", check_fields=False, mode="before")
    def _normalise(cls, v: Any, info: Any) -> Any:  # noqa: D401
        """Normalize common primitive types before validation."""
        if not info.field_name:
            return v

        # Bolt Optimization: Avoid function call overhead in hot path
        try:
            return _NORMALIZERS[cls][info.field_name](v)  # type: ignore[index]
        except KeyError:
            return _get_normalizer(cls, info.field_name)(v)  # type: ignore[arg-type]
