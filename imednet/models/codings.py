from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Coding(JsonModel):
    study_key: str = Field("", alias="studyKey")
    site_name: str = Field("", alias="siteName")
    site_id: int = Field(0, alias="siteId")
    subject_id: int = Field(0, alias="subjectId")
    subject_key: str = Field("", alias="subjectKey")
    form_id: int = Field(0, alias="formId")
    form_name: str = Field("", alias="formName")
    form_key: str = Field("", alias="formKey")
    revision: int = Field(0, alias="revision")
    record_id: int = Field(0, alias="recordId")
    variable: str = Field("", alias="variable")
    value: str = Field("", alias="value")
    coding_id: int = Field(0, alias="codingId")
    code: str = Field("", alias="code")
    coded_by: str = Field("", alias="codedBy")
    reason: str = Field("", alias="reason")
    dictionary_name: str = Field("", alias="dictionaryName")
    dictionary_version: str = Field("", alias="dictionaryVersion")
    date_coded: datetime = Field(default_factory=datetime.now, alias="dateCoded")
