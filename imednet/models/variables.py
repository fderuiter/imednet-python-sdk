import datetime
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Variable:
    study_key: str
    variable_id: int
    variable_type: str
    variable_name: str
    sequence: int
    revision: int
    disabled: bool
    date_created: datetime.datetime
    date_modified: datetime.datetime
    form_id: int
    variable_oid: str
    deleted: bool
    form_key: str
    form_name: str
    label: str
    blinded: bool

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Variable":
        """
        Create a Variable instance from JSON data.

        Args:
            data: Dictionary containing variable data from the API

        Returns:
            Variable instance with the data
        """
        # Parse datetime strings
        date_created = (
            datetime.datetime.fromisoformat(data.get("dateCreated", "").replace(" ", "T"))
            if data.get("dateCreated")
            else datetime.datetime.now()
        )

        date_modified = (
            datetime.datetime.fromisoformat(data.get("dateModified", "").replace(" ", "T"))
            if data.get("dateModified")
            else datetime.datetime.now()
        )

        return cls(
            study_key=data.get("studyKey", ""),
            variable_id=data.get("variableId", 0),
            variable_type=data.get("variableType", ""),
            variable_name=data.get("variableName", ""),
            sequence=data.get("sequence", 0),
            revision=data.get("revision", 0),
            disabled=data.get("disabled", False),
            date_created=date_created,
            date_modified=date_modified,
            form_id=data.get("formId", 0),
            variable_oid=data.get("variableOid", ""),
            deleted=data.get("deleted", False),
            form_key=data.get("formKey", ""),
            form_name=data.get("formName", ""),
            label=data.get("label", ""),
            blinded=data.get("blinded", False),
        )
