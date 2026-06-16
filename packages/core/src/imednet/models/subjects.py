from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class SubjectKeyword(JsonModel):
    """A keyword or tag associated with a subject."""

    keyword_id: int | None = Field(default=None, alias="keywordId")
    keyword_key: str | None = Field(default=None, alias="keywordKey")
    keyword_name: str | None = Field(default=None, alias="keywordName")
    date_added: str | None = Field(default=None, alias="dateAdded")


SubjectKeyword = ModelEngine.get_model('SubjectKeyword', SubjectKeyword)


class Subject(JsonModel):
    """A subject (participant) in a study, with status and site info."""

    subject_oid: str | None = Field(default=None, alias="subjectOid")
    enrollment_start_date: str | None = Field(default=None, alias="enrollmentStartDate")
    keywords: list[SubjectKeyword] = Field(default_factory=list)


Subject = ModelEngine.get_model('Subject', Subject)
