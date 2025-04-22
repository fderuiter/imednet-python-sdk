"""Client for interacting with the Studies endpoint."""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.study import StudyModel

from ._base import ResourceClient


class StudiesClient(ResourceClient):
    """Client for the Studies API resource.

    Provides methods for interacting with study-related endpoints,
    such as listing studies.
    """

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

        Raises:
            ImednetSdkException: If the API request fails.
            ApiError: For specific API-related errors (4xx, 5xx).
            AuthenticationError: If authentication fails (401).
            AuthorizationError: If authorization fails (403).
            NotFoundError: If the resource is not found (404).
            RateLimitError: If rate limits are exceeded (429).
            ValidationError: If request validation fails (400 with code 1000).
            BadRequestError: For general bad requests (400).
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
