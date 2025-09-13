from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field

from .json_base import JsonModel


class SubjectKeyword(JsonModel):
    """Represents a keyword or tag associated with a subject."""

    keyword_name: str = Field("", alias="keywordName", description="The name of the keyword.")
    keyword_key: str = Field("", alias="keywordKey", description="The key of the keyword.")
    keyword_id: int = Field(0, alias="keywordId", description="The ID of the keyword.")
    date_added: datetime = Field(
        default_factory=datetime.now,
        alias="dateAdded",
        description="The date the keyword was added.",
    )


class Subject(JsonModel):
    """Represents a subject (participant) in a study, including status and site information."""

    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    subject_id: int = Field(0, alias="subjectId", description="The ID of the subject.")
    subject_oid: str = Field("", alias="subjectOid", description="The OID of the subject.")
    subject_key: str = Field("", alias="subjectKey", description="The key of the subject.")
    subject_status: str = Field(
        "", alias="subjectStatus", description="The current status of the subject."
    )
    site_id: int = Field(0, alias="siteId", description="The ID of the site.")
    site_name: str = Field("", alias="siteName", description="The name of the site.")
    deleted: bool = Field(
        False, alias="deleted", description="Indicates if the subject is deleted."
    )
    enrollment_start_date: datetime = Field(
        default_factory=datetime.now,
        alias="enrollmentStartDate",
        description="The date the subject's enrollment started.",
    )
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the subject was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the subject was last modified.",
    )
    keywords: List[SubjectKeyword] = Field(
        default_factory=list, alias="keywords", description="A list of keywords for the subject."
    )
