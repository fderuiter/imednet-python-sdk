"""API client for interacting with the iMednet Intervals endpoints.

This module provides the `IntervalsClient` class for accessing interval definitions
within a specific study via the iMednet API.
"""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.interval import IntervalModel

from ._base import ResourceClient


class IntervalsClient(ResourceClient):
    """Provides methods for accessing iMednet interval definitions.

    This client interacts with endpoints under `/api/v1/edc/studies/{study_key}/intervals`.
    It is accessed via the `imednet_sdk.client.ImednetClient.intervals` property.
    """

    def list_intervals(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[IntervalModel]]:
        """Retrieves a list of interval definitions for a specific study.

        Corresponds to the `GET /api/v1/edc/studies/{studyKey}/intervals` endpoint.
        Supports standard pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            page: The index of the page to return (0-based). Defaults to 0.
            size: The number of items per page. Defaults to 25, maximum 500.
            sort: The property to sort by, optionally including direction
                  (e.g., 'intervalName,asc', 'intervalSequence,desc').
            filter: The filter criteria to apply (e.g., 'intervalSequence>5',
                    'intervalName=="Screening"'). Refer to iMednet API docs for syntax.
            **kwargs: Additional keyword arguments passed directly as query parameters
                      to the API request.

        Returns:
            An `ApiResponse` object containing a list of `IntervalModel` instances
            representing the interval definitions, along with pagination/metadata details.

        Raises:
            ValueError: If `study_key` is empty or not provided.
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, invalid permissions).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/intervals"
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if sort is not None:
            params["sort"] = sort
        if filter is not None:
            params["filter"] = filter

        # Pass any additional kwargs directly to the underlying request method
        params.update(kwargs)

        # Use self._get instead of self._client._get
        return self._get(endpoint, params=params, response_model=ApiResponse[List[IntervalModel]])
