from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v):
        """
        If no timestamp or empty, default to now();
        if string, normalize space to 'T' and parse ISO.
        """
        if not v:
            return datetime.now()
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace(" ", "T"))
        return v

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Variable:
        """
        Create a Variable instance from a JSON-like dict,
        honoring the same parsing logic as the original.
        """
        return cls.model_validate(data)
