"""Models describing data queries and associated comments."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validators import (
    parse_bool,
    parse_datetime,
    parse_int_or_default,
    parse_list_or_default,
    parse_str_or_default,
)


class QueryComment(BaseModel):
    sequence: int = Field(0, alias="sequence")
    annotation_status: str = Field("", alias="annotationStatus")
    user: str = Field("", alias="user")
    comment: str = Field("", alias="comment")
    closed: bool = Field(False, alias="closed")
    date: datetime = Field(default_factory=datetime.now, alias="date")

    # Allow instantiation via field names or aliases
    model_config = ConfigDict(populate_by_name=True)

    @field_validator("annotation_status", "user", "comment", mode="before")
    def _fill_strs(cls, v: Any) -> str:
        return parse_str_or_default(v)

    @field_validator("sequence", mode="before")
    def _fill_ints(cls, v: Any) -> int:
        return parse_int_or_default(v)

    @field_validator("date", mode="before")
    def _parse_date(cls, v: str | datetime) -> datetime:
        return parse_datetime(v)

    @field_validator("closed", mode="before")
    def parse_bool_field(cls, v: Any) -> bool:
        return parse_bool(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "QueryComment":
        """
        Create a QueryComment instance from a JSON-like dict.
        """
        return cls.model_validate(data)


class Query(BaseModel):
    """Data model describing a query raised on study data."""

    study_key: str = Field("", alias="studyKey")
    subject_id: int = Field(0, alias="subjectId")
    subject_oid: str = Field("", alias="subjectOid")
    annotation_type: str = Field("", alias="annotationType")
    annotation_id: int = Field(0, alias="annotationId")
    type: Optional[str] = Field(None, alias="type")
    description: str = Field("", alias="description")
    record_id: int = Field(0, alias="recordId")
    variable: str = Field("", alias="variable")
    subject_key: str = Field("", alias="subjectKey")
    date_created: datetime = Field(default_factory=datetime.now, alias="dateCreated")
    date_modified: datetime = Field(default_factory=datetime.now, alias="dateModified")
    query_comments: List[QueryComment] = Field(default_factory=list, alias="queryComments")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator(
        "study_key",
        "subject_oid",
        "annotation_type",
        "description",
        "variable",
        "subject_key",
        mode="before",
    )
    def _fill_strs(cls, v: Any) -> str:
        return parse_str_or_default(v)

    @field_validator("subject_id", "annotation_id", "record_id", mode="before")
    def _fill_ints(cls, v: Any) -> int:
        return parse_int_or_default(v)

    @field_validator("query_comments", mode="before")
    def _fill_list(cls, v: Any) -> list[QueryComment]:
        return parse_list_or_default(v)

    @field_validator("date_created", "date_modified", mode="before")
    def _parse_datetimes(cls, v: str | datetime) -> datetime:
        return parse_datetime(v)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Query":
        """
        Create a Query instance from a JSON-like dict, including nested comments.
        """
        return cls.model_validate(data)
