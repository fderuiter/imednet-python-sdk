from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Form(JsonModel):
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
