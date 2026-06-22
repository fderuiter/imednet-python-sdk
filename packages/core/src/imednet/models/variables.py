"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class Variable(JsonModel):
    """TODO: Add docstring."""

    study_key: Optional[str] = Field(default=None, alias="studyKey")
    variable_id: Optional[int] = Field(default=None, alias="variableId")
    variable_type: Optional[str] = Field(default=None, alias="variableType")
    variable_name: Optional[str] = Field(default=None, alias="variableName")
    sequence: Optional[int] = Field(default=None, alias="sequence")
    revision: Optional[int] = Field(default=None, alias="revision")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")
    form_id: Optional[int] = Field(default=None, alias="formId")
    form_key: Optional[str] = Field(default=None, alias="formKey")
    form_name: Optional[str] = Field(default=None, alias="formName")
    label: Optional[str] = Field(default=None, alias="label")
    variable_oid: Optional[str] = Field(default=None, alias="variableOid")

