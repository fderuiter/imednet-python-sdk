"""API client for interacting with the iMe        endpoint = f"/api/v1/edc/studies/{study_key}/visits"
        # Use self._get instead of self._client._get
        response: ApiResponse[List[VisitModel]] = self._get(
            endpoint, params=kwargs, response_model=ApiResponse[List[VisitModel]]
        )
        return responset Visits endpoints.

This module provides the `VisitsClient` class for accessing visit definitions
within a specific study via the iMednet API.
"""

from typing import List

from ..models._common import ApiResponse
from ..models.visit import VisitModel
from ._base import ResourceClient


class VisitsClient(ResourceClient):
    """Provides methods for accessing iMednet visit definitions.

    This client interacts with endpoints under
    `/api/v1/edc/studies/{study_key}/visits`.
    It is accessed via the
    `imednet_sdk.client.ImednetClient.visits` property.
    """

    def list_visits(self, study_key: str, **kwargs) -> ApiResponse[List[VisitModel]]:
        """Retrieves a list of visit definitions for a specific study.

        Corresponds to the `GET /api/v1/edc/studies/{studyKey}/visits` endpoint.
        Supports standard pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            **kwargs: Additional keyword arguments passed directly as query parameters
                      to the API request, such as `page`, `size`, `sort`, `filter`.
                      Refer to the iMednet API documentation for available options.

        Returns:
            An `ApiResponse` object containing a list of `VisitModel` instances
            representing the visit definitions, along with pagination/metadata details.

        Raises:
            ValueError: If `study_key` is empty or not provided.
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, invalid permissions).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")  # Match test expectation

        endpoint = f"/api/v1/edc/studies/{study_key}/visits"
        # Use self._get instead of self._client._get
        response = self._get(endpoint, params=kwargs, response_model=ApiResponse[List[VisitModel]])
        return response
