"""
Pydantic model and API client for iMednet “variables”.

This module provides:

- `VariableModel`: a Pydantic model representing a variable (form field) definition.
- `VariablesClient`: an API client for the `/api/v1/edc/studies/{study_key}/variables` endpoint.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from ._base import ApiResponse, ResourceClient


class VariableModel(BaseModel):
    """Represents the definition of a variable (field) on an eCRF in iMednet."""

    studyKey: str = Field(..., description="Unique Study Key")
    variableId: int = Field(..., description="Mednet Variable ID")
    variableType: str = Field(..., description="Type of the variable (e.g., radioField, textField)")
    variableName: str = Field(..., description="Name of the variable on the eCRF")
    sequence: int = Field(..., description="User-defined sequence of the variable")
    revision: int = Field(..., description="Number of modifications to the variable metadata")
    disabled: bool = Field(False, description="Flag indicating if the variable is disabled")
    dateCreated: datetime = Field(..., description="Creation date of the variable")
    dateModified: datetime = Field(..., description="Last modification date of the variable")
    formId: int = Field(..., description="Mednet Form ID")
    variableOid: Optional[str] = Field(None, description="Client-assigned Variable OID")
    deleted: bool = Field(False, description="Flag indicating if the variable is deleted")
    formKey: str = Field(..., description="Form key")
    formName: str = Field(..., description="Name of the eCRF")
    label: str = Field(..., description="User-defined field label")
    blinded: bool = Field(False, description="Flag indicating if the variable is blinded")


class VariablesClient(ResourceClient):
    """Provides methods for accessing iMednet variable definitions.

    Interacts with endpoints under `/api/v1/edc/studies/{study_key}/variables`.
    Access via `ImednetClient.variables`.
    """

    def list_variables(self, study_key: str, **kwargs) -> ApiResponse[List[VariableModel]]:
        """Retrieves variable definitions for a specific study.

        GET /api/v1/edc/studies/{studyKey}/variables
        Supports pagination, filtering (e.g. `filter='formKey=="AE"'`), and sorting via kwargs.

        Args:
            study_key: Unique identifier for the study.
            **kwargs: Passed as query params (`page`, `size`, `sort`, `filter`, etc.).

        Returns:
            ApiResponse[List[VariableModel]] with variables and pagination metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors (network, auth, permissions).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/variables"
        response: ApiResponse[List[VariableModel]] = self._get(
            endpoint,
            params=kwargs,
            response_model=ApiResponse[List[VariableModel]],
        )
        return response
