from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field

from imednet.models.json_base import JsonModel


class SubjectKeyword(JsonModel):
    """A keyword or tag associated with a subject."""

    keyword_name: str = Field("", alias="keywordName")
    keyword_key: str = Field("", alias="keywordKey")
    keyword_id: int = Field(0, alias="keywordId")
    date_added: datetime = Field(default_factory=datetime.now, alias="dateAdded")

    pass


class Subject(JsonModel):
    """A subject (participant) in a study, with status and site info."""

    study_key: str = Field("", alias="studyKey")
    subject_id: int = Field(0, alias="subjectId")
    subject_oid: str = Field("", alias="subjectOid")
    subject_key: str = Field("", alias="subjectKey")
    subject_status: str = Field("", alias="subjectStatus")
    site_id: int = Field(0, alias="siteId")
    site_name: str = Field("", alias="siteName")
    deleted: bool = Field(False, alias="deleted")
    enrollment_start_date: datetime = Field(
        default_factory=datetime.now, alias="enrollmentStartDate"
    )
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")
    keywords: List[SubjectKeyword] = Field(default_factory=list, alias="keywords")

    pass
