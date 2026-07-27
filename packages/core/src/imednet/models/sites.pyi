"""Site (study location) models for iMedNet."""

from __future__ import annotations

from imednet.models.base import ImednetBaseModel
from imednet.models.engine import ModelEngine

from typing import Any, Optional


class Site(ImednetBaseModel):
    """A site participating in a study."""

    study_key: Optional[str]
    site_id: Optional[int]
    site_name: Optional[str]
    site_enrollment_status: Optional[str]
    date_created: Optional[str]
    date_modified: Optional[str]
    last_updated: Optional[str]
