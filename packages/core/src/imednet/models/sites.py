"""Site (study location) models for iMedNet."""

from __future__ import annotations

from datetime import datetime

from msgspec import field as Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel


class Site(JsonModel, kw_only=True, omit_defaults=True):
    """A site participating in a study."""

    pass


Site = ModelEngine.get_model('Site', Site)
