from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class RecordRevision(JsonModel):
    """Historical version of a record including change reason and user."""

    pass


RecordRevision = ModelEngine.get_model('RecordRevision', RecordRevision)
