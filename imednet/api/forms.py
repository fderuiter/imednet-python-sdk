"""
Pydantic model and API client for iMednet “forms”.

This module provides:

- `FormModel`: a Pydantic model representing an eCRF definition.
- `FormsClient`: an API client for the `/api/v1/edc/studies/{study_key}/forms` endpoint.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel, Field

from ._base import ApiResponse, ResourceClient


class FormModel(BaseModel):
    """Represents the definition of an electronic Case Report Form (eCRF) in iMednet."""

    studyKey: str = Field(..., description="Unique study key")
    formId: int = Field(..., description="Mednet Form ID")
    formKey: str = Field(..., description="Form key")
    formName: str = Field(..., description="Name of the eCRF")
    formType: str = Field(..., description="eCRF type (e.g., 'Subject', 'Site', 'Common')")
    revision: int = Field(..., description="Number of modifications to the form metadata")
    embeddedLog: bool = Field(False, description="Embedded log enabled")
    enforceOwnership: bool = Field(False, description="Enforce ownership enabled")
    userAgreement: bool = Field(False, description="User agreement required")
    subjectRecordReport: bool = Field(False, description="Subject record report enabled")
    unscheduledVisit: bool = Field(False, description="Allowed in unscheduled visits")
    otherForms: bool = Field(False, description="Included in other forms")
    eproForm: bool = Field(False, description="Is an ePRO form")
    allowCopy: bool = Field(True, description="Copy allowed")
    disabled: bool = Field(False, description="Form is disabled (soft delete)")
    dateCreated: datetime = Field(..., description="Timestamp when the form was created")
    dateModified: datetime = Field(..., description="Timestamp when the form was last modified")


class FormsClient(ResourceClient):
    """Provides methods for accessing iMednet form definitions."""

    def list_forms(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[FormModel]]:
        """Retrieves a list of form definitions for a specific study.

        GET /api/v1/edc/studies/{studyKey}/forms
        Supports pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            page: Zero-based page index.
            size: Number of items per page.
            sort: Sort expression (e.g., 'formName,asc').
            filter: Filter expression (e.g., 'formType=="Subject"').
            **kwargs: Additional query parameters.

        Returns:
            ApiResponse[List[FormModel]] containing forms and pagination metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors.
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/forms"
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if sort is not None:
            params["sort"] = sort
        if filter is not None:
            params["filter"] = filter
        params.update(kwargs)

        # Cast the result to the expected type
        return cast(
            ApiResponse[List[FormModel]],
            self._get(
                endpoint,
                params=params,
                response_model=ApiResponse[List[FormModel]],
            ),
        )
