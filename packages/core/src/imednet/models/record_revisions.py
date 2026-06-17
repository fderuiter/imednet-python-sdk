from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class RecordRevision(JsonModel):
    """Historical version of a record including change reason and user."""

    record_revision_id: Optional[str] = Field(None, alias="recordRevisionId")


RecordRevision = ModelEngine.get_model('RecordRevision', RecordRevision)
