"""Study metadata models for iMedNet."""

from __future__ import annotations

from datetime import datetime

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Study(JsonModel, kw_only=True, omit_defaults=True):
    """Represents a clinical study and its metadata."""


Study = ModelEngine.get_model('Study', Study)
