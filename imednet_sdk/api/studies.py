"""API client for interacting with the iMednet Studies endpoints.

This module provides the `StudiesClient` class for accessing study-level
information via the iMednet API.
"""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.study import StudyModel

from ._base import ResourceClient


class StudiesClient(ResourceClient):
    """Provides methods for accessing iMednet study data.

    This client interacts with endpoints under `/api/v1/edc/studies`.
    It is accessed via the `imednet_sdk.client.ImednetClient.studies` property.
    """

    def list_studies(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[StudyModel]]:
        """Retrieves a list of studies accessible to the authenticated user.

        Corresponds to the `GET /api/v1/edc/studies` endpoint.
        Supports standard pagination, filtering, and sorting parameters.

        Args:
            page: The index of the page to return (0-based). Defaults to 0.
            size: The number of items per page. Defaults to 25, maximum 500.
            sort: The property to sort by, optionally including direction
                  (e.g., 'studyKey,asc', 'studyName,desc').
            filter: The filter criteria to apply (e.g., 'studyKey=="DEMO"',
                    'studyStatus=="Active"'). Refer to iMednet API docs for syntax.
            **kwargs: Additional keyword arguments passed directly as query parameters
                      to the API request.

        Returns:
            An `ApiResponse` object containing a list of `StudyModel` instances
            representing the studies, along with pagination/metadata details.

        Raises:
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, invalid permissions).
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

        # Use the helper method from the base class
        # Note: The type hint for response_model needs to match what _get expects.
        # If ApiResponse is not a Pydantic model itself, this might need adjustment.
        # Assuming ApiResponse[List[StudyModel]] can be handled by TypeAdapter.
        return self._get(
            endpoint,
            params=params,
            response_model=ApiResponse[List[StudyModel]],  # Ensure correct response model typing
        )

    # Add other study-related methods here (e.g., get_study_details)
    # def get_study(self, study_key: str, **kwargs: Any) -> StudyModel:
    #     """Retrieve details for a specific study."""
    #     if not study_key:
    #         raise ValueError("study_key cannot be empty")
    #     endpoint = f"/api/v1/edc/studies/{study_key}"
    #     # Assuming the single study endpoint returns the model directly, not wrapped in ApiResponse
    #     return self._get(endpoint, response_model=StudyModel, **kwargs)
