"""Client for interacting with the Intervals endpoint."""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.interval import IntervalModel

from ._base import ResourceClient


class IntervalsClient(ResourceClient):
    """Client for the Intervals API resource."""

    def list_intervals(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[IntervalModel]]:
        """
        Retrieve a list of intervals for a specific study.

        Corresponds to `GET /api/v1/edc/studies/{studyKey}/intervals`.

        Args:
            study_key: The key of the study for which to list intervals.
            page: Index page to return. Default is 0.
            size: Number of items per page. Default is 25. Max 500.
            sort: Property to sort by (e.g., 'intervalName,asc').
            filter: Filter criteria (e.g., 'intervalSequence>5').
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            An ApiResponse containing a list of IntervalModel objects.

        Raises:
            ValueError: If study_key is empty or None.
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

        return self._client._get(
            endpoint, params=params, response_model=ApiResponse[List[IntervalModel]]
        )
