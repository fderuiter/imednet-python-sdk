"""Models for subjects and participant keywords."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class SubjectKeyword(JsonModel):
    """A keyword or tag associated with a subject."""

    pass


SubjectKeyword = ModelEngine.get_model("SubjectKeyword", SubjectKeyword)


class Subject(JsonModel):
    """A subject (participant) in a study, with status and site info."""

    pass


Subject = ModelEngine.get_model("Subject", Subject)
