"""Site (study location) models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.base import ImednetBaseModel

class Site(ImednetBaseModel):
    """A site participating in a study."""

    pass

    study_key: Optional[str]
    site_id: Optional[int]
    site_name: Optional[str]
    site_enrollment_status: Optional[str]
    date_created: Optional[str]
    date_modified: Optional[str]
