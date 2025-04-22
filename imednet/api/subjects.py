"""
Pydantic models and API client for iMednet “subjects”.

This module provides:

- `KeywordModel` and `SubjectModel`: Pydantic models representing subject data.
- `SubjectsClient`: an API client for the `/api/v1/edc/studies/{study_key}/subjects` endpoint.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel, Field

from ._base import ApiResponse, ResourceClient


class KeywordModel(BaseModel):
    """Represents a keyword associated with a subject in iMednet."""

    keywordName: str = Field(..., description="Name of the keyword")
    keywordKey: str = Field(..., description="Unique key for the keyword")
    keywordId: int = Field(..., description="Unique ID for the keyword")
    dateAdded: datetime = Field(..., description="Date when the keyword was added")


class SubjectModel(BaseModel):
    """Represents a participant (subject) enrolled in a study in iMednet."""

    studyKey: str = Field(..., description="Unique study key for the given study")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: Optional[str] = Field(None, description="Client-assigned subject OID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    subjectStatus: str = Field(..., description="Current status of the subject")
    siteId: int = Field(..., description="Mednet Site ID")
    siteName: str = Field(..., description="Name of the site")
    enrollmentStartDate: Optional[datetime] = Field(
        None, description="Date when the subject enrollment started"
    )
    deleted: bool = Field(False, description="Indicates whether the subject was deleted")
    dateCreated: datetime = Field(..., description="Date when the subject record was created")
    dateModified: datetime = Field(..., description="Last modification date of the subject record")
    keywords: Optional[List[KeywordModel]] = Field(
        default=None, description="List of keywords associated with the subject"
    )


class SubjectsClient(ResourceClient):
    """Provides methods for accessing iMednet subject data."""

    def list_subjects(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[SubjectModel]]:
        """Retrieves a list of subjects for a specific study.

        GET /api/v1/edc/studies/{studyKey}/subjects
        Supports pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            page: Zero-based page index.
            size: Number of items per page.
            sort: Sort property and direction (e.g. 'dateCreated,desc').
            filter: Filter expression (e.g. 'siteId==123').
            **kwargs: Additional query parameters.

        Returns:
            ApiResponse[List[SubjectModel]] containing subjects and metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors (network, auth, permissions).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/subjects"
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

        # Cast the result to the expected type
        response = cast(
            ApiResponse[List[SubjectModel]],
            self._get(
                endpoint,
                params=params,
                response_model=ApiResponse[List[SubjectModel]],
            ),
        )
        return response
