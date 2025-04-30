from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_datetime, parse_int_or_default, parse_str_or_default


class Study(BaseModel):
    """Represents a Study in the iMedNet system.
    This model represents a study in the iMedNet system, including information
    about the sponsor, study identifiers, name, description, type, and
    creation/modification dates.
        sponsor_key (str): The key identifier for the study sponsor. Defaults to "".
        study_key (str): The unique key identifier for the study. Defaults to "".
        study_id (int): The numeric identifier for the study. Defaults to 0.
        study_name (str): The name of the study. Defaults to "".
        study_description (str): A description of the study. Defaults to "".
        study_type (str): The type of the study. Defaults to "".
        date_created (datetime): The date and time when the study was created.
            Defaults to current time.
        date_modified (datetime): The date and time when the study was last modified.
            Defaults to current time.
        Study: A Study object representing a study in the iMedNet system.
    """

    sponsor_key: str = Field("", alias="sponsorKey")
    study_key: str = Field("", alias="studyKey")
    study_id: int = Field(0, alias="studyId")
    study_name: str = Field("", alias="studyName")
    study_description: str = Field("", alias="studyDescription")
    study_type: str = Field("", alias="studyType")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "sponsor_key", "study_key", "study_name", "study_description", "study_type", mode="before"
    )
    def _fill_strs(cls, v: str) -> str:
        return parse_str_or_default(v)

    @field_validator("study_id", mode="before")
    def _fill_ints(cls, v: int) -> int:
        return parse_int_or_default(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_dates(cls, v: str | datetime) -> datetime:
        return parse_datetime(v)
