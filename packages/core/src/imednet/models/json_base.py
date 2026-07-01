"""Base Pydantic model with data normalization and drift detection logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Dict, Union, get_args, get_origin

import msgspec
from typing import TypeVar

from imednet.utils.validators import (
    is_missing_value,
    parse_bool,
    parse_datetime,
    parse_dict_or_default,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)

_NORMALIZERS: Dict[type, Dict[str, Callable[[Any], Any]]] = {}


def _identity(v: Any) -> Any:
    """Return the value as-is."""
    return v


def _optional_str(v: Any) -> Any:
    """Convert value to string, returning None if missing."""
    return None if is_missing_value(v) else parse_str_or_default(v)


def _optional_int(v: Any) -> Any:
    """Convert value to int, returning None if missing."""
    return None if is_missing_value(v) else parse_int_or_default(v)


def _optional_bool(v: Any) -> Any:
    """Convert value to bool, returning None if missing."""
    return None if is_missing_value(v) else parse_bool(v)


def _optional_datetime(v: Any) -> Any:
    """Convert value to datetime, returning None if missing."""
    return None if is_missing_value(v) else parse_datetime(v)


def _extract_single_item(v: Any) -> Any:
    """Extract the first item if a list is provided where an object was expected."""
    if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
        import logging

        logging.getLogger(__name__).warning(
            "Structural shift detected: API returned a list where an object was expected. Coercing by extracting the first item."
        )
        return v[0]
    return v


import types


def _get_normalizer(cls: type[msgspec.Struct], field_name: str) -> Callable[[Any], Any]:
    """Determine the appropriate normalization function for a model field.

    Analyzes type hints to select a parser for strings, integers, booleans,
    datetimes, or nested models.
    """
    if cls in _NORMALIZERS and field_name in _NORMALIZERS[cls]:
        return _NORMALIZERS[cls][field_name]

    field = next((f for f in msgspec.structs.fields(cls) if f.name == field_name), None)
    if field is None:
        return _identity
    annotation = field.type
    origin = get_origin(annotation)
    optional = False

    if origin is Union or origin is getattr(types, "UnionType", type(None)):
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
        normalizer = _optional_str if optional else parse_str_or_default
    elif annotation is int:
        normalizer = _optional_int if optional else parse_int_or_default
    elif annotation is bool:
        normalizer = _optional_bool if optional else parse_bool
    elif annotation is datetime:
        normalizer = _optional_datetime if optional else parse_datetime
    elif isinstance(annotation, type) and issubclass(annotation, msgspec.Struct):
        normalizer = _extract_single_item

    if cls not in _NORMALIZERS:
        _NORMALIZERS[cls] = {}
    _NORMALIZERS[cls][field_name] = normalizer
    return normalizer


import os

_drift_reported: set[str] = set()




def _strip_strings(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _strip_strings(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_strip_strings(item) for item in data]
    elif isinstance(data, str):
        return data.strip()
    return data

T = TypeVar("T", bound="JsonModel")



def _strip_strings(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _strip_strings(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_strip_strings(item) for item in data]
    elif isinstance(data, str):
        return data.strip()
    return data

T = TypeVar("T", bound="JsonModel")

class JsonModel(msgspec.Struct, kw_only=True, omit_defaults=True):
    """Base model with shared JSON parsing helpers."""

    @classmethod
    def from_json(cls: type[T], data: Any) -> T:
        """Validate data coming from JSON APIs."""
        data = _strip_strings(data)
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                import logging
                logging.getLogger(__name__).warning(
                    f"Structural shift detected: API returned a list where an object ({cls.__name__}) was expected. Coercing by extracting the first item."
                )
                data = data[0]
            elif len(data) == 0:
                import logging
                logging.getLogger(__name__).warning(
                    f"Structural shift detected: API returned an empty list where an object ({cls.__name__}) was expected. Coercing to empty dict."
                )
                data = {}

        if isinstance(data, dict):
            import logging
            logger = logging.getLogger("imednet.drift")

            defined_fields = set()
            for f in msgspec.structs.fields(cls):
                defined_fields.add(f.name)
                if f.encode_name:
                    defined_fields.add(f.encode_name)

            for name in dir(cls):
                if isinstance(getattr(cls, name), property):
                    defined_fields.add(name)

            incoming_keys = set(data.keys())

            unexpected_fields = incoming_keys - defined_fields
            if unexpected_fields:
                msg = f"Drift detected (additive): {cls.__name__} received unexpected fields: {', '.join(sorted(unexpected_fields))}"
                if msg not in _drift_reported:
                    _drift_reported.add(msg)
                    logger.warning(msg)

            missing_fields = []
            for f in msgspec.structs.fields(cls):
                if f.default is msgspec.NODEFAULT and f.default_factory is msgspec.NODEFAULT:
                    if f.name not in incoming_keys and (
                        not f.encode_name or f.encode_name not in incoming_keys
                    ):
                        missing_fields.append(f.name)
            if missing_fields:
                msg = f"Drift detected (destructive): {cls.__name__} missing required fields: {', '.join(sorted(missing_fields))}"
                if msg not in _drift_reported:
                    _drift_reported.add(msg)
                    logger.warning(msg)

            # Normalization
            normalized_data = dict(data)
            for f in msgspec.structs.fields(cls):
                key = f.encode_name if f.encode_name and f.encode_name in normalized_data else f.name
                if key in normalized_data:
                    v = normalized_data[key]
                    if isinstance(v, str):
                        v = v.strip()
                    try:
                        norm = _NORMALIZERS[cls][f.name]
                    except KeyError:
                        norm = _get_normalizer(cls, f.name)
                    normalized_data[key] = norm(v)
            data = normalized_data

        try:
            return msgspec.convert(data, type=cls, strict=False)
        except Exception as e:
            import logging
            msg = f"Drift detected (destructive): {cls.__name__} validation failed: {e}"
            if msg not in _drift_reported:
                _drift_reported.add(msg)
                logging.getLogger("imednet.drift").warning(msg)
            raise
