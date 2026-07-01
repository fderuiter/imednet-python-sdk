"""Record revision history models for iMedNet."""

from __future__ import annotations

from datetime import datetime

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class RecordRevision(JsonModel, kw_only=True, omit_defaults=True):
    """Historical version of a record including change reason and user."""

    pass


RecordRevision = ModelEngine.get_model('RecordRevision', RecordRevision)
