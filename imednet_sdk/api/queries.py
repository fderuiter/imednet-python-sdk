"""API client for interacting with the iMednet Queries endpoints.

This module provides the `QueriesClient` class for accessing query data
(data clarifications, annotations) within a specific study via the iMednet API.
"""

from typing import List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.query import QueryModel

from ._base import ResourceClient


class QueriesClient(ResourceClient):
    """Provides methods for accessing iMednet query data.

    This client interacts with endpoints under `/api/v1/edc/studies/{study_key}/queries`.
    It is accessed via the `imednet_sdk.client.ImednetClient.queries` property.
    """

    def list_queries(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> ApiResponse[List[QueryModel]]:
        """Retrieves a list of queries for a specific study.

        Corresponds to the `GET /api/v1/edc/studies/{studyKey}/queries` endpoint.
        Supports standard pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            page: The index of the page to return (0-based). Defaults to 0.
            size: The number of items per page. Defaults to 25, maximum 500.
            sort: The property to sort by, optionally including direction
                  (e.g., 'annotationId,asc', 'queryStatus,desc').
            filter: The filter criteria to apply (e.g., 'variable=="AETERM"'
                    'queryStatus=="Open"'). Refer to iMednet API docs for syntax.

        Returns:
            An `ApiResponse` object containing a list of `QueryModel` instances
            representing the queries, along with pagination/metadata details.

        Raises:
            ValueError: If `study_key` is empty or not provided.
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, invalid permissions).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/queries"

        params = {
            "page": page,
            "size": size,
            "sort": sort,
            "filter": filter,
        }
        # Remove None values to avoid sending empty query parameters
        params = {k: v for k, v in params.items() if v is not None}

        # Use self._get instead of self._client._get
        return self._get(
            endpoint, params=params, response_model=ApiResponse[List[QueryModel]]
        )
