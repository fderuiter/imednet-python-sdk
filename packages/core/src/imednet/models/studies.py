"""Study metadata models for iMedNet."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.base import ImednetBaseModel


class Study(ImednetBaseModel):
    """Represents a clinical study and its metadata."""


Study = ModelEngine.get_model('Study', Study)
