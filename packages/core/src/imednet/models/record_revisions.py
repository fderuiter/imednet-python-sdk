"""Record revision history models for iMedNet."""

from __future__ import annotations

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine


class RecordRevision(ImednetBaseModel):
    """Historical version of a record including change reason and user."""


RecordRevision = ModelEngine.get_model('RecordRevision', RecordRevision)
