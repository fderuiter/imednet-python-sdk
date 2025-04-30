from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_bool, parse_datetime, parse_int_or_default, parse_str_or_default


class Form(BaseModel):
    """
    A Pydantic model representing a Form entity in the system.
    This class inherits from BaseModel and defines various attributes of a form including
    its identifiers, properties, and metadata.
    Attributes:
        study_key (str): Key identifier for the study this form belongs to
        form_id (int): Unique identifier for the form
        form_key (str): Key identifier for the form
        form_name (str): Display name of the form
        form_type (str): Type classification of the form
        revision (int): Revision number of the form
        embedded_log (bool): Whether the form has embedded logging
        enforce_ownership (bool): Whether ownership rules are enforced
        user_agreement (bool): Whether user agreement is required
        subject_record_report (bool): Whether the form is a subject record report
        unscheduled_visit (bool): Whether the form is for unscheduled visits
        other_forms (bool): Whether the form relates to other forms
        epro_form (bool): Whether the form is an ePRO form
        allow_copy (bool): Whether copying is allowed for this form
        disabled (bool): Whether the form is disabled
        date_created (datetime): Timestamp of form creation
        date_modified (datetime): Timestamp of last modification
    The model includes field validators for proper type conversion and data parsing,
    and supports JSON serialization/deserialization through Pydantic's model_validate.
    """

    study_key: str = Field("", alias="studyKey")
    form_id: int = Field(0, alias="formId")
    form_key: str = Field("", alias="formKey")
    form_name: str = Field("", alias="formName")
    form_type: str = Field("", alias="formType")
    revision: int = Field(0, alias="revision")
    embedded_log: bool = Field(False, alias="embeddedLog")
    enforce_ownership: bool = Field(False, alias="enforceOwnership")
    user_agreement: bool = Field(False, alias="userAgreement")
    subject_record_report: bool = Field(False, alias="subjectRecordReport")
    unscheduled_visit: bool = Field(False, alias="unscheduledVisit")
    other_forms: bool = Field(False, alias="otherForms")
    epro_form: bool = Field(False, alias="eproForm")
    allow_copy: bool = Field(False, alias="allowCopy")
    disabled: bool = Field(False, alias="disabled")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("study_key", "form_key", "form_name", "form_type", mode="before")
    def _fill_strs(cls, v: Any) -> str:
        return parse_str_or_default(v)

    @field_validator("form_id", "revision", mode="before")
    def _fill_ints(cls, v: Any) -> int:
        return parse_int_or_default(v)

    @field_validator(
        "embedded_log",
        "enforce_ownership",
        "user_agreement",
        "subject_record_report",
        "unscheduled_visit",
        "other_forms",
        "epro_form",
        "allow_copy",
        "disabled",
        mode="before",
    )
    def _parse_bools(cls, v: Any) -> bool:
        return parse_bool(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v: Any) -> datetime:
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Form":
        """
        Create a Form instance from JSON-like dict.
        """
        return cls.model_validate(data)
