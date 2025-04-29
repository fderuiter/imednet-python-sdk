from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import parse_datetime, parse_int_or_default, parse_str_or_default


class Coding(BaseModel):
    """
    A class representing a medical coding instance in a clinical study.
    This class models coding data for clinical study records, including study identifiers,
    subject information, form details, and coding-specific attributes.
    Attributes:
        study_key (str): The unique identifier for the study.
        site_name (str): The name of the study site.
        site_id (int): The numerical identifier for the study site.
        subject_id (int): The numerical identifier for the subject.
        subject_key (str): The unique identifier for the subject.
        form_id (int): The numerical identifier for the form.
        form_name (str): The name of the form.
        form_key (str): The unique identifier for the form.
        revision (int): The revision number of the form.
        record_id (int): The numerical identifier for the record.
        variable (str): The variable name being coded.
        value (str): The value being coded.
        coding_id (int): The numerical identifier for the coding instance.
        code (str): The assigned code.
        coded_by (str): The identifier of the person who performed the coding.
        reason (str): The reason for the coding decision.
        dictionary_name (str): The name of the coding dictionary used.
        dictionary_version (str): The version of the coding dictionary used.
        date_coded (datetime): The timestamp when the coding was performed.
    Note:
        This model uses Pydantic's BaseModel and supports both field names and their aliases
        for data population. All string and integer fields have default values, and datetime
        fields default to the current time if not specified.
    """

    study_key: str = Field("", alias="studyKey")
    site_name: str = Field("", alias="siteName")
    site_id: int = Field(0, alias="siteId")
    subject_id: int = Field(0, alias="subjectId")
    subject_key: str = Field("", alias="subjectKey")
    form_id: int = Field(0, alias="formId")
    form_name: str = Field("", alias="formName")
    form_key: str = Field("", alias="formKey")
    revision: int = Field(0, alias="revision")
    record_id: int = Field(0, alias="recordId")
    variable: str = Field("", alias="variable")
    value: str = Field("", alias="value")
    coding_id: int = Field(0, alias="codingId")
    code: str = Field("", alias="code")
    coded_by: str = Field("", alias="codedBy")
    reason: str = Field("", alias="reason")
    dictionary_name: str = Field("", alias="dictionaryName")
    dictionary_version: str = Field("", alias="dictionaryVersion")
    date_coded: datetime = Field(default_factory=datetime.now, alias="dateCoded")

    # allow population by field names as well as aliases
    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "study_key",
        "site_name",
        "subject_key",
        "form_name",
        "form_key",
        "variable",
        "value",
        "code",
        "coded_by",
        "reason",
        "dictionary_name",
        "dictionary_version",
        mode="before",
    )
    def _fill_strs(cls, v):
        return parse_str_or_default(v)

    @field_validator(
        "site_id", "subject_id", "form_id", "revision", "record_id", "coding_id", mode="before"
    )
    def _fill_ints(cls, v):
        return parse_int_or_default(v)

    @field_validator("date_coded", mode="before")
    def _parse_date_coded(cls, v: str | datetime) -> datetime:
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> Coding:
        """
        Create a Coding instance from a JSON-like dict.
        """
        return cls.model_validate(data)
