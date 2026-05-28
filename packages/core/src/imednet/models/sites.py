from __future__ import annotations

from imednet.models.engine import ModelEngine

from datetime import datetime

from pydantic import Field

from imednet.models.json_base import JsonModel


class Site(JsonModel):
    """A site participating in a study."""


    pass
Site = ModelEngine.get_model('Site', Site)

