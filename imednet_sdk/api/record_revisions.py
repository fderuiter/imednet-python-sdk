"""
Pydantic model and API client for iMednet “record revisions”.

This module provides:

- `RecordRevisionModel`:
    a Pydantic model representing a single entry in a records audit trail.
- `RecordRevisionsClient`:
    an API client for the `/api/v1/edc/studies/{study_key}/record-revisions` endpoint.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ._base import ApiResponse, ResourceClient


class RecordRevisionModel(BaseModel):
    """Represents a single entry in the audit trail (revision history) of a record."""

    studyKey: str = Field(..., description="Unique study key for the given study")
    recordRevisionId: int = Field(
        ..., description="Unique system identifier for the record revision"
    )
    recordId: int = Field(..., description="Unique system identifier for the related record")
    recordOid: str = Field(..., description="Client-assigned record OID")
    recordRevision: int = Field(..., description="Record revision number")
    dataRevision: int = Field(..., description="Data revision number")
    recordStatus: str = Field(..., description="User-defined record status")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: str = Field(..., description="Client-assigned subject OID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    siteId: int = Field(..., description="Unique system identifier for the related site")
    formKey: str = Field(..., description="Form key")
    intervalId: int = Field(..., description="Unique system identifier for the interval")
    role: str = Field(..., description="Role of the user who saved the record revision")
    user: str = Field(..., description="Username of the user who saved the record revision")
    reasonForChange: Optional[str] = Field(
        None, description="Reason for the change made in the record revision"
    )
    deleted: bool = Field(False, description="Indicates whether the record was deleted")
    dateCreated: datetime = Field(..., description="Date when the record revision was created")


class RecordRevisionsClient(ResourceClient):
    """Provides methods for accessing iMednet record revision history."""

    def list_record_revisions(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[RecordRevisionModel]]:
        """Retrieves a list of record revisions for a specific study.

        GET /api/v1/edc/studies/{studyKey}/record-revisions
        Supports pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            page: Zero-based page index.
            size: Number of items per page.
            sort: Sort expression (e.g., 'recordId,asc').
            filter: Filter expression (e.g., 'subjectId=="S-001"').
            **kwargs: Additional query parameters.

        Returns:
            ApiResponse[List[RecordRevisionModel]] containing revisions and metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors.
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/record-revisions"
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if sort is not None:
            params["sort"] = sort
        if filter is not None:
            params["filter"] = filter
        params.update(kwargs)

        return self._get(
            endpoint,
            params=params,
            response_model=ApiResponse[List[RecordRevisionModel]],
        )
