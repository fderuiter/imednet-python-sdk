"""Site (study location) models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine

class Site(ImednetBaseModel):
    """A site participating in a study."""

    pass

    study_key: str | None
    site_id: int | None
    site_name: str | None
    site_enrollment_status: str | None
    date_created: str | None
    date_modified: str | None
