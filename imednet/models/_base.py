from __future__ import annotations

from datetime import datetime
from typing import Any, Union, get_args, get_origin

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
        field = cls.model_fields[info.field_name]
        annotation = field.annotation
        origin = get_origin(annotation)
        optional = False
        if origin is Union:
            args = [a for a in get_args(annotation) if a is not type(None)]
            if len(args) == 1:
                annotation = args[0]
                origin = get_origin(annotation)
                optional = True

        if origin is list:
            return parse_list_or_default(v)
        if origin is dict:
            return parse_dict_or_default(v)

        if annotation is str:
            if optional and v is None:
                return None
            return parse_str_or_default(v)
        if annotation is int:
            if optional and v is None:
                return None
            return parse_int_or_default(v)
        if annotation is bool:
            if optional and v is None:
                return None
            return parse_bool(v)
        if annotation is datetime:
            if optional and not v:
                return None
            return parse_datetime(v)
        return v
