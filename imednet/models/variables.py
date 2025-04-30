from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_bool, parse_datetime, parse_int_or_default, parse_str_or_default


class Variable(BaseModel):
    """Variable model representing a study variable within iMedNet.
    This class represents a variable within a study in iMedNet, containing metadata about
    the variable such as its ID, type, name, and associated form details.
        study_key (str): The key identifier for the study this variable belongs to.
        variable_id (int): The unique identifier for this variable.
        variable_type (str): The type of the variable (e.g., "number", "text", "date").
        variable_name (str): The name of the variable.
        sequence (int): The sequence order of the variable.
        revision (int): The revision number of the variable.
        disabled (bool): Whether the variable is disabled.
        date_created (datetime): The date and time when the variable was created.
        date_modified (datetime): The date and time when the variable was last modified.
        form_id (int): The ID of the form this variable belongs to.
        variable_oid (Optional[str]): The OID (Object Identifier) of the variable, if available.
        deleted (bool): Whether the variable has been marked as deleted.
        form_key (str): The key identifier of the form this variable belongs to.
        form_name (str): The name of the form this variable belongs to.
        label (str): The display label for the variable.
        blinded (bool): Whether the variable is blinded (hidden from certain users).
        Variable: An instance of the Variable class.
    """

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
    def _fill_strs(cls, v: Any) -> str:
        return parse_str_or_default(v)

    @field_validator("variable_id", "sequence", "revision", "form_id", mode="before")
    def _fill_ints(cls, v: Any) -> int:
        return parse_int_or_default(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v: str | datetime) -> datetime:
        return parse_datetime(v)

    @field_validator("disabled", "deleted", "blinded", mode="before")
    def parse_bool_field(cls, v: Any) -> bool:
        return parse_bool(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Variable":
        """
        Create a Variable instance from a JSON-like dict,
        honoring the same parsing logic as the original.
        """
        return cls.model_validate(data)
