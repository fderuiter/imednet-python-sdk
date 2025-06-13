from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from imednet.utils.validators import (
    parse_bool,
    parse_datetime,
    parse_int_or_default,
    parse_str_or_default,
)


class Variable(BaseModel):
    study_key: str = Field("", alias="studyKey")
    variable_id: int = Field(0, alias="variableId")
    variable_type: str = Field("", alias="variableType")
    variable_name: str = Field("", alias="variableName")
    sequence: int = Field(0, alias="sequence")
    revision: int = Field(0, alias="revision")
    disabled: bool = Field(False, alias="disabled")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")
    form_id: int = Field(0, alias="formId")
    variable_oid: Optional[str] = Field(None, alias="variableOid")
    deleted: bool = Field(False, alias="deleted")
    form_key: str = Field("", alias="formKey")
    form_name: str = Field("", alias="formName")
    label: str = Field("", alias="label")
    blinded: bool = Field(False, alias="blinded")

    # allow population by field names as well as aliases
    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "study_key",
        "variable_type",
        "variable_name",
        "form_key",
        "form_name",
        "label",
        mode="before",
    )
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator("variable_id", "sequence", "revision", "form_id", mode="before")
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        return parse_datetime(v)

    @field_validator("disabled", "deleted", "blinded", mode="before")
    def parse_bool_field(cls, v):
        return parse_bool(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Variable:
        """
        Create a Variable instance from a JSON-like dict,
        honoring the same parsing logic as the original.
        """
        return cls.model_validate(data)
