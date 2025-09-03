from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Coding(JsonModel):
    """Represents a medical coding entry in the system."""

    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    site_name: str = Field("", alias="siteName", description="The name of the site.")
    site_id: int = Field(0, alias="siteId", description="The ID of the site.")
    subject_id: int = Field(0, alias="subjectId", description="The ID of the subject.")
    subject_key: str = Field("", alias="subjectKey", description="The key of the subject.")
    form_id: int = Field(0, alias="formId", description="The ID of the form.")
    form_name: str = Field("", alias="formName", description="The name of the form.")
    form_key: str = Field("", alias="formKey", description="The key of the form.")
    revision: int = Field(0, alias="revision", description="The revision number of the form.")
    record_id: int = Field(0, alias="recordId", description="The ID of the record.")
    variable: str = Field(
        "", alias="variable", description="The name of the variable that was coded."
    )
    value: str = Field("", alias="value", description="The original value that was coded.")
    coding_id: int = Field(0, alias="codingId", description="The ID of the coding entry.")
    code: str = Field("", alias="code", description="The code that was assigned.")
    coded_by: str = Field("", alias="codedBy", description="The user who performed the coding.")
    reason: str = Field("", alias="reason", description="The reason for the coding decision.")
    dictionary_name: str = Field(
        "",
        alias="dictionaryName",
        description="The name of the coding dictionary used.",
    )
    dictionary_version: str = Field(
        "",
        alias="dictionaryVersion",
        description="The version of the coding dictionary used.",
    )
    date_coded: datetime = Field(
        default_factory=datetime.now,
        alias="dateCoded",
        description="The date the coding was performed.",
    )
