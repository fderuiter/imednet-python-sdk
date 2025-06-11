from __future__ import annotations

from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


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
