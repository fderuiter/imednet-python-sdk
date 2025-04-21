"""API client for interacting with the Queries endpoint."""

from typing import List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.query import QueryModel

from ._base import ResourceClient


class QueriesClient(ResourceClient):
    """Client for the Queries endpoint."""

    def list_queries(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
    ) -> ApiResponse[List[QueryModel]]:
        """Fetches a list of queries for a given study.

        Args:
            study_key: The key of the study to fetch queries for.
            page: The page number to retrieve (default: 0).
            size: The number of items per page (default: 25, max: 500).
            sort: The sorting criteria (e.g., 'annotationId,asc').
            filter: The filtering criteria (e.g., 'variable==aeterm').

        Returns:
            An ApiResponse containing a list of QueryModel objects.

        Raises:
            ValueError: If study_key is empty.
            ImednetApiException: For API-related errors.
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

        response_json = self._client.get(endpoint, params=params)

        # Assuming the response structure matches ApiResponse[List[QueryModel]]
        # Pydantic will handle the parsing and validation
        return ApiResponse[List[QueryModel]].model_validate(response_json)
