"""Site (study location) models for iMedNet."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.base import ImednetBaseModel


class Site(ImednetBaseModel):
    """A site participating in a study."""

    pass


Site = ModelEngine.get_model('Site', Site)
