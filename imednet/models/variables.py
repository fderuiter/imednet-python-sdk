from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class Variable(JsonModel):
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

    pass
