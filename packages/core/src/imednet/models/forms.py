"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class Form(JsonModel):
    """TODO: Add docstring."""

    study_key: Optional[str] = Field(default=None, alias="studyKey")
    form_id: Optional[int] = Field(default=None, alias="formId")
    form_key: Optional[str] = Field(default=None, alias="formKey")
    form_name: Optional[str] = Field(default=None, alias="formName")
    form_type: Optional[str] = Field(default=None, alias="formType")
    revision: Optional[int] = Field(default=None, alias="revision")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")
    disabled: Optional[bool] = Field(default=None, alias="disabled")
    subject_record_report: Optional[bool] = Field(default=None, alias="subjectRecordReport")
    unscheduled_visit: Optional[bool] = Field(default=None, alias="unscheduledVisit")
    epro_form: Optional[bool] = Field(default=None, alias="eproForm")
    allow_copy: Optional[bool] = Field(default=None, alias="allowCopy")

