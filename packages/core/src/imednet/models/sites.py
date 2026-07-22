"""Site (study location) models for iMedNet."""

from __future__ import annotations

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine


class Site(ImednetBaseModel):
    """A site participating in a study."""


Site = ModelEngine.get_model('Site', Site)
