from __future__ import annotations

from typing import Generic, List, TypeVar, Dict, Any

from pydantic import BaseModel, ConfigDict, Field

from .base import IMNModel

T = TypeVar("T")


class Meta(BaseModel):
    """Top-level metadata block included in API responses."""

    status: str
    method: str
    path: str
    timestamp: str
    error: Dict[str, Any] | None = None


class Pagination(IMNModel):
    """Pagination block returned by the API."""

    current_page: int = Field(..., alias="currentPage")
    page_size: int = Field(..., alias="pageSize")
    total_pages: int = Field(..., alias="totalPages")
    total_records: int = Field(..., alias="totalRecords")


class Envelope(IMNModel, Generic[T]):
    """Generic API envelope model."""

    metadata: Meta
    pagination: Pagination
    data: List[T]

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """Dump model using camelCase aliases by default."""

        kwargs.setdefault("by_alias", True)
        return super().model_dump(**kwargs)


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


class StudiesEnvelope(Envelope[Study]):
    pass


class SitesEnvelope(Envelope[Site]):
    pass


class RecordsEnvelope(Envelope[Record]):
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

    """Sort order item used in pagination metadata."""

    # ``property`` is a reserved keyword in Python, use ``property_`` internally
    property_: str = Field(alias="property")
    direction: str

    model_config = ConfigDict(populate_by_name=True)
