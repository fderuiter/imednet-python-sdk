"""
Pydantic model and API client for iMednet “codings”.

This module provides:

- `CodingModel`: a Pydantic model representing coding data.
- `CodingsClient`: an API client for the `/api/v1/edc/studies/{study_key}/codings` endpoint.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from ._base import ApiResponse, ResourceClient


class CodingModel(BaseModel):
    """Represents a standardized coding applied to a data point in iMednet."""

    studyKey: str = Field(..., description="Unique Study Key")
    siteName: str = Field(..., description="Name of the site")
    siteId: int = Field(..., description="Unique site ID")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    formId: int = Field(..., description="Mednet Form ID")
    formName: str = Field(..., description="Name of the eCRF")
    formKey: str = Field(..., description="Form key")
    revision: int = Field(..., description="Number of modifications to the coding metadata")
    recordId: int = Field(..., description="Unique system identifier for the record")
    variable: str = Field(..., description="Name of the variable on the eCRF")
    value: str = Field(..., description="Value entered")
    codingId: int = Field(..., description="Mednet Coding ID")
    code: str = Field(..., description="Standardized code")
    codedBy: str = Field(..., description="User who recorded the code")
    reason: Optional[str] = Field(None, description="Reason for the coding")
    dictionaryName: str = Field(..., description="Name of the coding dictionary (e.g., MedDRA)")
    dictionaryVersion: str = Field(..., description="Version of the coding dictionary")
    dateCoded: datetime = Field(..., description="Date when the code was added")


class CodingsClient(ResourceClient):
    """Provides methods for accessing iMednet coding data."""

    def list_codings(self, study_key: str, **kwargs) -> ApiResponse[List[CodingModel]]:
        """Retrieves a list of codings for a specific study.

        GET /api/v1/edc/studies/{study_key}/codings
        Supports pagination, filtering, and sorting via kwargs.

        Args:
            study_key: The unique identifier for the study.
            **kwargs: Query parameters (e.g., page, size, sort, filter).

        Returns:
            ApiResponse[List[CodingModel]] containing codings and metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors.
        """
        if not study_key:
            raise ValueError("study_key is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/codings"
        return self._get(
            endpoint,
            params=kwargs,
            response_model=ApiResponse[List[CodingModel]],
        )
