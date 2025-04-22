"""Client for interacting with the Sites endpoint."""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.site import SiteModel  # Assuming SiteModel exists

from ._base import ResourceClient


class SitesClient(ResourceClient):
    """Client for the Sites API resource.

    Provides methods for interacting with site-related endpoints,
    such as listing sites within a study.
    """

    def list_sites(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[SiteModel]]:
        """
        Retrieve a list of sites for a specific study.

        Corresponds to `GET /api/v1/edc/studies/{studyKey}/sites`.

        Args:
            study_key: The key of the study for which to list sites.
            page: Index page to return. Default is 0.
            size: Number of items per page. Default is 25. Max 500.
            sort: Property to sort by (e.g., 'siteName,asc').
            filter: Filter criteria (e.g., 'siteName=="Central Hospital"').
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            An ApiResponse containing a list of SiteModel objects.

        Raises:
            ValueError: If study_key is empty or None.
            ImednetSdkException: If the API request fails.
            ApiError: For specific API-related errors (4xx, 5xx).
            AuthenticationError: If authentication fails (401).
            AuthorizationError: If authorization fails (403).
            NotFoundError: If the resource is not found (404).
            RateLimitError: If rate limits are exceeded (429).
            ValidationError: If request validation fails (400 with code 1000).
            BadRequestError: For general bad requests (400).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/sites"
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
        # Assuming ApiResponse[List[SiteModel]] can be handled by TypeAdapter.
        return self._get(
            endpoint,
            params=params,
            response_model=ApiResponse[List[SiteModel]],  # Ensure correct response model typing
        )

    # Add other site-related methods here (e.g., get_site_details)
    # def get_site(self, study_key: str, site_key: str, **kwargs: Any) -> SiteModel:
    #     """Retrieve details for a specific site within a study."""
    #     if not study_key:
    #         raise ValueError("study_key cannot be empty")
    #     if not site_key:
    #         raise ValueError("site_key cannot be empty")
    #     endpoint = f"/api/v1/edc/studies/{study_key}/sites/{site_key}"
    #     # Assuming the single site endpoint returns the model directly
    #     return self._get(endpoint, response_model=SiteModel, **kwargs)
