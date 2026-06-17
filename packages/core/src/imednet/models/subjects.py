from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class SubjectKeyword(JsonModel):
    """A keyword or tag associated with a subject."""

    keyword_name: Optional[str] = Field(None, alias="keywordName")
    keyword_key: Optional[str] = Field(None, alias="keywordKey")
    keyword_id: Optional[int] = Field(None, alias="keywordId")
    date_added: Optional[str] = Field(None, alias="dateAdded")


SubjectKeyword = ModelEngine.get_model('SubjectKeyword', SubjectKeyword)


class Subject(JsonModel):
    """A subject (participant) in a study, with status and site info."""

    subject_oid: Optional[str] = Field(None, alias="subjectOid")
    enrollment_start_date: Optional[str] = Field(None, alias="enrollmentStartDate")
    keywords: Optional[List[SubjectKeyword]] = None
    subject_key: Optional[str] = Field(None, alias="subjectKey")
    subject_status: Optional[str] = Field(None, alias="subjectStatus")


Subject = ModelEngine.get_model('Subject', Subject)
