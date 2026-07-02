"""Models for subjects and participant keywords."""

from __future__ import annotations

from datetime import datetime
from typing import List

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


SubjectKeyword = ModelEngine.get_model('SubjectKeyword', SubjectKeyword)


class Subject(ImednetBaseModel):
    """A subject (participant) in a study, with status and site info."""

    keywords: List[SubjectKeyword] = Field(default_factory=list, alias="keywords")

    pass


Subject = ModelEngine.get_model('Subject', Subject)
