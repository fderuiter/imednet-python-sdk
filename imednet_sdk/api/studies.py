"""Client for interacting with the Studies endpoint."""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.study import StudyModel

from ._base import ResourceClient


class StudiesClient(ResourceClient):
    """Client for the Studies API resource."""

    def list_studies(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[StudyModel]]:
        """
        Retrieve a list of studies based on specified criteria.

        Corresponds to `GET /api/v1/edc/studies`.

        Args:
            page: Index page to return. Default is 0.
            size: Number of items per page. Default is 25. Max 500.
            sort: Property to sort by (e.g., 'studyKey,asc').
            filter: Filter criteria (e.g., 'studyKey=="DEMO"').
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            An ApiResponse containing a list of StudyModel objects.
        """
        endpoint = "/api/v1/edc/studies"
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

        return self._client._get( # Correctly calls the base client's _get method
            endpoint, params=params, response_model=ApiResponse[List[StudyModel]] # Specifies the correct response model
        )
