"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class SubjectKeyword(JsonModel):
    """TODO: Add docstring."""

    keyword_name: Optional[str] = Field(default=None, alias="keywordName")

    pass


class Subject(JsonModel):
    """TODO: Add docstring."""

    study_key: Optional[str] = Field(default=None, alias="studyKey")
    subject_id: Optional[int] = Field(default=None, alias="subjectId")
    subject_key: Optional[str] = Field(default=None, alias="subjectKey")
    subject_status: Optional[str] = Field(default=None, alias="subjectStatus")
    site_id: Optional[int] = Field(default=None, alias="siteId")
    site_name: Optional[str] = Field(default=None, alias="siteName")
    deleted: Optional[bool] = Field(default=None, alias="deleted")
    date_created: Optional[str] = Field(default=None, alias="dateCreated")
    date_modified: Optional[str] = Field(default=None, alias="dateModified")
    keywords: List[SubjectKeyword] = Field(default_factory=list, alias="keywords")
    enrollment_start_date: Optional[str] = Field(default=None, alias="enrollmentStartDate")

    pass
