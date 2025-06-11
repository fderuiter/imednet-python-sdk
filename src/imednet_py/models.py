from __future__ import annotations

from typing import Generic, List, TypeVar, Dict, Any

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Meta(BaseModel):
    """Top-level metadata block included in API responses."""

    status: str
    method: str
    path: str
    timestamp: str
    error: Dict[str, Any] | None = None


class Envelope(BaseModel, Generic[T]):
    """Generic API envelope model."""

    model_config = ConfigDict(extra="allow")

    data: T


class Study(BaseModel):
    """Study model (fields are loosely typed)."""

    model_config = ConfigDict(extra="allow")

    key: str | None = None


class Site(BaseModel):
    """Site model."""

    model_config = ConfigDict(extra="allow")

    key: str | None = None


class Record(BaseModel):
    """Record model."""

    model_config = ConfigDict(extra="allow")

    key: str | None = None


class StudiesEnvelope(Envelope[List[Study]]):
    pass


class SitesEnvelope(Envelope[List[Site]]):
    pass


class RecordsEnvelope(Envelope[List[Record]]):
    pass


class Sort(BaseModel):
    """Sorting information used in paginated responses."""

    property: str = Field(alias="property")
    direction: str


class Pagination(BaseModel):
    """Pagination details included in API responses."""

    current_page: int = Field(alias="currentPage")
    size: int
    total_pages: int = Field(alias="totalPages")
    total_elements: int = Field(alias="totalElements")
    sort: List[Sort]
