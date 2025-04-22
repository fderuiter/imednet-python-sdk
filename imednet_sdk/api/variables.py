"""API client for interacting with the iMednet Variables endpoints.

This module provides the `VariablesClient` class for accessing variable definitions
(metadata about data fields) within a specific study via the iMednet API.
"""

from typing import List

from ..models._common import ApiResponse
from ..models.variable import VariableModel
from ._base import ResourceClient


class VariablesClient(ResourceClient):
    """Provides methods for accessing iMednet variable definitions.

    This client interacts with endpoints under `/api/v1/edc/studies/{study_key}/variables`.
    It is accessed via the `imednet_sdk.client.ImednetClient.variables` property.
    Variable definitions are crucial for understanding the structure and types of
    data stored in records.
    """

    def list_variables(self, study_key: str, **kwargs) -> ApiResponse[List[VariableModel]]:
        """Retrieves a list of variable definitions for a specific study.

        Corresponds to the `GET /api/v1/edc/studies/{studyKey}/variables` endpoint.
        Supports standard pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            **kwargs: Additional keyword arguments passed directly as query parameters
                      to the API request, such as `page`, `size`, `sort`, `filter`.
                      Filtering might be useful to get variables for a specific form
                      (e.g., `filter='formKey=="AE"'`). Refer to the iMednet API
                      documentation for available options.

        Returns:
            An `ApiResponse` object containing a list of `VariableModel` instances
            representing the variable definitions, along with pagination/metadata details.

        Raises:
            ValueError: If `study_key` is empty or not provided.
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, invalid permissions).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")  # Match test expectation

        endpoint = f"/api/v1/edc/studies/{study_key}/variables"
        # Use self._get instead of self._client._get
        return self._get(endpoint, params=kwargs, response_model=ApiResponse[List[VariableModel]])
