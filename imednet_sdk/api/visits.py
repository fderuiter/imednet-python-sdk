"""
Pydantic model and API client for iMednet “visits”.

This module provides:

- `VisitModel`: a Pydantic model representing a subject visit instance.
- `VisitsClient`: an API client for the `/api/v1/edc/studies/{study_key}/visits` endpoint.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from ._base import ApiResponse, ResourceClient


class VisitModel(BaseModel):
    """Represents a specific instance of a subject visit within a study schedule."""

    visitId: int = Field(..., description="Unique system identifier for the subject visit instance")
    studyKey: str = Field(..., description="Unique study key for the given study")
    intervalId: int = Field(..., description="Unique system identifier for the related interval")
    intervalName: str = Field(..., description="User-defined identifier for the related interval")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    startDate: date = Field(
        ..., description="Subject visit Start Date defined in interval visit window"
    )
    endDate: date = Field(
        ..., description="Subject visit End Date defined in interval visit window"
    )
    dueDate: Optional[date] = Field(
        None, description="Subject visit Due Date defined in interval visit window"
    )
    visitDate: date = Field(..., description="Actual date the visit occurred")
    visitDateForm: str = Field(..., description="Key of the form where the visitDate is recorded")
    visitDateQuestion: str = Field(..., description="Variable name where the visitDate is recorded")
    deleted: bool = Field(False, description="Subject visit deleted flag")
    dateCreated: datetime = Field(..., description="Timestamp when this visit was created")
    dateModified: datetime = Field(..., description="Timestamp when this visit was last modified")


class VisitsClient(ResourceClient):
    """Provides methods for accessing iMednet visit definitions.

    Interacts with endpoints under `/api/v1/edc/studies/{study_key}/visits`.
    Access via `ImednetClient.visits`.
    """

    def list_visits(self, study_key: str, **kwargs) -> ApiResponse[List[VisitModel]]:
        """Retrieve visit definitions for a given study.

        GET /api/v1/edc/studies/{studyKey}/visits
        Supports pagination, filtering, sorting via kwargs.

        Args:
            study_key: Unique identifier for the study.
            **kwargs: Passed as query params (e.g. page, size, sort, filter).

        Returns:
            ApiResponse[List[VisitModel]] with visits and metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors (network, auth, permissions).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/visits"
        response: ApiResponse[List[VisitModel]] = self._get(
            endpoint,
            params=kwargs,
            response_model=ApiResponse[List[VisitModel]],
        )
        return response
