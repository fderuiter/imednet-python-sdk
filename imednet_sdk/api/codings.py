"""API client for interacting with the iMednet Codings endpoints.

This module provides the `CodingsClient` class for accessing coding-related
data within a specific study via the iMednet API.
"""

from typing import List

from ..models._common import ApiResponse
from ..models.coding import CodingModel
from ._base import ResourceClient


class CodingsClient(ResourceClient):
    """Provides methods for accessing iMednet coding data.

    This client interacts with endpoints under `/api/v1/edc/studies/{study_key}/codings`.
    It is accessed via the `imednet_sdk.client.ImednetClient.codings` property.
    """

    def list_codings(self, study_key: str, **kwargs) -> ApiResponse[List[CodingModel]]:
        """Retrieves a list of codings for a specific study.

        Corresponds to the `GET /api/v1/edc/studies/{study_key}/codings` endpoint.
        Supports standard pagination, filtering, and sorting parameters via kwargs.

        Args:
            study_key: The unique identifier for the study.
            **kwargs: Additional keyword arguments passed as query parameters to the API,
                      such as `page`, `size`, `sort`, `filter`.
                      Refer to the iMednet API documentation for available options.

        Returns:
            An `ApiResponse` object containing a list of `CodingModel` instances
            and pagination/metadata details.

        Raises:
            ValueError: If `study_key` is empty or not provided.
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, invalid permissions).
        """
        if not study_key:
            raise ValueError("study_key is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/codings"
        # Use self._get instead of self._client._get
        return self._get(
            endpoint, params=kwargs, response_model=ApiResponse[List[CodingModel]]
        )
