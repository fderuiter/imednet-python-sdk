from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class Variable(JsonModel):
    """Represents a variable within a form."""

    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    variable_id: int = Field(0, alias="variableId", description="The ID of the variable.")
    variable_type: str = Field("", alias="variableType", description="The type of the variable.")
    variable_name: str = Field("", alias="variableName", description="The name of the variable.")
    sequence: int = Field(0, alias="sequence", description="The sequence number of the variable.")
    revision: int = Field(0, alias="revision", description="The revision number of the variable.")
    disabled: bool = Field(
        False, alias="disabled", description="Indicates if the variable is disabled."
    )
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the variable was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the variable was last modified.",
    )
    form_id: int = Field(
        0,
        alias="formId",
        description="The ID of the form the variable belongs to.",
    )
    variable_oid: Optional[str] = Field(
        None, alias="variableOid", description="The OID of the variable."
    )
    deleted: bool = Field(
        False, alias="deleted", description="Indicates if the variable is deleted."
    )
    form_key: str = Field(
        "", alias="formKey", description="The key of the form the variable belongs to."
    )
    form_name: str = Field(
        "", alias="formName", description="The name of the form the variable belongs to."
    )
    label: str = Field("", alias="label", description="The label of the variable.")
    blinded: bool = Field(
        False, alias="blinded", description="Indicates if the variable is blinded."
    )
