"""
Pydantic models and API client for iMednet “queries”.

This module provides:

- `QueryCommentModel` and `QueryModel`: Pydantic models representing query annotations.
- `QueriesClient`: an API client for the `/api/v1/edc/studies/{study_key}/queries` endpoint.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel, Field

from ._base import ApiResponse, ResourceClient


class QueryCommentModel(BaseModel):
    """Represents a single comment or action taken on a query in iMednet."""

    sequence: int = Field(..., description="Query comment sequence")
    user: str = Field(..., description="User performing the query action")
    annotationStatus: str = Field(..., description="User-defined query status")
    comment: str = Field(..., description="User comment applied during query action")
    closed: bool = Field(False, description="Indicates if the query was closed")
    date: datetime = Field(..., description="Date of the query comment")


class QueryModel(BaseModel):
    """Represents a query (annotation) raised against data in iMednet."""

    studyKey: str = Field(..., description="Unique study key")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: str = Field(..., description="Client-assigned subject OID")
    annotationType: str = Field(..., description="User-defined identifier for query type")
    annotationId: int = Field(..., description="Unique system identifier for the query")
    type: Optional[str] = Field(None, description="System text identifier for query type/location")
    description: str = Field(..., description="Query description")
    recordId: Optional[int] = Field(None, description="Unique system identifier for record")
    variable: Optional[str] = Field(None, description="User-defined field identifier")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    dateCreated: datetime = Field(..., description="Date when the query was created")
    dateModified: datetime = Field(..., description="Date when the query was modified")
    queryComments: List[QueryCommentModel] = Field(
        ..., description="List of comments and actions on the query"
    )


class QueriesClient(ResourceClient):
    """Provides methods for accessing iMednet query data."""

    def list_queries(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[QueryModel]]:
        """Retrieves a list of queries for a specific study.

        GET /api/v1/edc/studies/{studyKey}/queries
        Supports pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            page: Zero-based page index.
            size: Number of items per page.
            sort: Sort expression (e.g., 'annotationId,asc').
            filter: Filter expression (e.g., 'queryStatus=="Open"').
            **kwargs: Additional query parameters.

        Returns:
            ApiResponse[List[QueryModel]] containing queries and pagination metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors.
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/queries"
        params: Dict[str, Any] = {
            **{
                k: v
                for k, v in {"page": page, "size": size, "sort": sort, "filter": filter}.items()
                if v is not None
            },
            **kwargs,
        }

        # Cast the result to the expected type
        response = cast(
            ApiResponse[List[QueryModel]],
            self._get(
                endpoint,
                params=params,
                response_model=ApiResponse[List[QueryModel]],
            ),
        )
        return response
