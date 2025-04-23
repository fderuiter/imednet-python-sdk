import datetime
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Form:
    study_key: str
    form_id: int
    form_key: str
    form_name: str
    form_type: str
    revision: int
    embedded_log: bool
    enforce_ownership: bool
    user_agreement: bool
    subject_record_report: bool
    unscheduled_visit: bool
    other_forms: bool
    epro_form: bool
    allow_copy: bool
    disabled: bool
    date_created: datetime.datetime
    date_modified: datetime.datetime

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Form":
        """
        Create a Form instance from JSON data.

        Args:
            data: Dictionary containing form data from the API

        Returns:
            Form instance with the data
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
            form_id=data.get("formId", 0),
            form_key=data.get("formKey", ""),
            form_name=data.get("formName", ""),
            form_type=data.get("formType", ""),
            revision=data.get("revision", 0),
            embedded_log=data.get("embeddedLog", False),
            enforce_ownership=data.get("enforceOwnership", False),
            user_agreement=data.get("userAgreement", False),
            subject_record_report=data.get("subjectRecordReport", False),
            unscheduled_visit=data.get("unscheduledVisit", False),
            other_forms=data.get("otherForms", False),
            epro_form=data.get("eproForm", False),
            allow_copy=data.get("allowCopy", False),
            disabled=data.get("disabled", False),
            date_created=date_created,
            date_modified=date_modified,
        )
