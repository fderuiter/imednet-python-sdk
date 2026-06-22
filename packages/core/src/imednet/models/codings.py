"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class Coding(JsonModel):
    """TODO: Add docstring."""

    study_key: Optional[str] = Field(default=None, alias="studyKey")
    site_name: Optional[str] = Field(default=None, alias="siteName")
    site_id: Optional[int] = Field(default=None, alias="siteId")
    subject_id: Optional[int] = Field(default=None, alias="subjectId")
    subject_key: Optional[str] = Field(default=None, alias="subjectKey")
    form_id: Optional[int] = Field(default=None, alias="formId")
    form_name: Optional[str] = Field(default=None, alias="formName")
    form_key: Optional[str] = Field(default=None, alias="formKey")
    record_id: Optional[int] = Field(default=None, alias="recordId")
    variable: Optional[str] = Field(default=None, alias="variable")
    value: Optional[str] = Field(default=None, alias="value")
    coding_id: Optional[int] = Field(default=None, alias="codingId")
    code: Optional[str] = Field(default=None, alias="code")
    coded_by: Optional[str] = Field(default=None, alias="codedBy")
    dictionary_name: Optional[str] = Field(default=None, alias="dictionaryName")
    dictionary_version: Optional[str] = Field(default=None, alias="dictionaryVersion")
    date_coded: Optional[str] = Field(default=None, alias="dateCoded")
