from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Form(JsonModel):
    """Represents a form (eCRF) in a study."""

    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    form_id: int = Field(0, alias="formId", description="The ID of the form.")
    form_key: str = Field("", alias="formKey", description="The key of the form.")
    form_name: str = Field("", alias="formName", description="The name of the form.")
    form_type: str = Field("", alias="formType", description="The type of the form.")
    revision: int = Field(0, alias="revision", description="The revision number of the form.")
    embedded_log: bool = Field(
        False, alias="embeddedLog", description="Indicates if the form has an embedded log."
    )
    enforce_ownership: bool = Field(
        False, alias="enforceOwnership", description="Indicates if ownership is enforced."
    )
    user_agreement: bool = Field(
        False, alias="userAgreement", description="Indicates if the form is a user agreement."
    )
    subject_record_report: bool = Field(
        False,
        alias="subjectRecordReport",
        description="Indicates if the form is a subject record report.",
    )
    unscheduled_visit: bool = Field(
        False,
        alias="unscheduledVisit",
        description="Indicates if the form is for an unscheduled visit.",
    )
    other_forms: bool = Field(
        False, alias="otherForms", description="Indicates if the form is an 'other' form."
    )
    epro_form: bool = Field(
        False, alias="eproForm", description="Indicates if the form is an ePRO form."
    )
    allow_copy: bool = Field(
        False, alias="allowCopy", description="Indicates if the form can be copied."
    )
    disabled: bool = Field(
        False, alias="disabled", description="Indicates if the form is disabled."
    )
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the form was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the form was last modified.",
    )
