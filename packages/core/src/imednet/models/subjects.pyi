"""Models for subjects and participant keywords."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.base import ImednetBaseModel

class SubjectKeyword(ImednetBaseModel):
    """A keyword or tag associated with a subject."""

    keyword_name: str = Field("", alias="keywordName")
    keyword_key: str = Field("", alias="keywordKey")
    keyword_id: int = Field(0, alias="keywordId")
    date_added: datetime = Field(default_factory=datetime.now, alias="dateAdded")

    pass

class Subject(ImednetBaseModel):
    """A subject (participant) in a study, with status and site info."""

    keywords: List[SubjectKeyword] = Field(default_factory=list, alias="keywords")

    pass

    study_key: Optional[str]
    subject_id: Optional[int]
    subject_key: Optional[str]
    subject_status: Optional[str]
    site_id: Optional[int]
    site_name: Optional[str]
    deleted: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
    enrollment_start_date: Any
    subject_oid: Any
