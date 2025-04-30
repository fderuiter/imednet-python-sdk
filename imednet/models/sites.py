from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_datetime, parse_int_or_default, parse_str_or_default


class Site(BaseModel):
    """
    Represents a clinical study site with associated metadata.

    Attributes:
        study_key (str): A unique identifier for the study to which the site belongs.
        site_id (int): A unique identifier for the site.
        site_name (str): The name of the site.
        site_enrollment_status (str): The enrollment status of the site (e.g., active, inactive).
        date_created (datetime): The timestamp when the site was created.
        date_modified (datetime): The timestamp when the site was last modified.
    """

    study_key: str = Field("", alias="studyKey")
    site_id: int = Field(0, alias="siteId")
    site_name: str = Field("", alias="siteName")
    site_enrollment_status: str = Field("", alias="siteEnrollmentStatus")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")

    # allow population by field names as well as aliases
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("study_key", "site_name", "site_enrollment_status", mode="before")
    def _fill_strs(cls, v: Any) -> str:
        return parse_str_or_default(v)

    @field_validator("site_id", mode="before")
    def _fill_ints(cls, v: Any) -> int:
        return parse_int_or_default(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v: str | datetime) -> datetime:
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Site":
        """
        Create a Site instance from JSON-like dict.
        """
        return cls.model_validate(data)
