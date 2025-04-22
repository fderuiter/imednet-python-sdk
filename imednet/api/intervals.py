"""
Pydantic models and API client for iMednet “intervals”.

This module provides:

- `IntervalFormModel` and `IntervalModel`:
    Pydantic models representing interval (visit) definitions.

- `IntervalsClient`:
    an API client for the `/api/v1/edc/studies/{study_key}/intervals` endpoint.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ._base import ApiResponse, ResourceClient


class IntervalFormModel(BaseModel):
    """Represents a simplified view of a form associated with an interval."""

    formId: int = Field(..., description="Unique numeric identifier for the form definition")
    formKey: str = Field(..., description="Unique string identifier for the form definition")
    formName: str = Field(..., description="Display name of the eCRF form")


class IntervalModel(BaseModel):
    """Represents the definition of an Interval (often synonymous with Visit) in iMednet."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    studyKey: str = Field(..., description="Unique study key")
    intervalId: int = Field(..., description="Unique system identifier for the interval definition")
    intervalName: str = Field(..., description="User-defined interval/visit name")
    intervalSequence: int = Field(..., description="User-defined sequence of the interval")
    intervalGroupId: int = Field(..., description="User-defined interval group ID")
    intervalGroupName: str = Field(..., description="User-defined interval group name")
    timeline: str = Field(..., description="Type of interval window (e.g., 'Static', 'Dynamic')")
    forms: List[IntervalFormModel] = Field(
        default_factory=list, description="List of forms associated with the interval"
    )
    disabled: bool = Field(False, description="Indicates if the interval definition is disabled")
    dateCreated: datetime = Field(..., description="Date when the interval definition was created")
    dateModified: datetime = Field(
        ..., description="Last modification date of the interval definition"
    )

    # Optional scheduling fields
    intervalDescription: Optional[str] = Field(None, description="Interval description")
    definedUsingInterval: Optional[str] = Field(
        None, description="Baseline interval name used for date calculations"
    )
    windowCalculationForm: Optional[str] = Field(
        None, description="Baseline form key used for date calculations"
    )
    windowCalculationDate: Optional[str] = Field(
        None, description="Baseline variable name used for date calculations"
    )
    actualDateForm: Optional[str] = Field(
        None, description="Form key containing the actual date field"
    )
    actualDate: Optional[str] = Field(None, description="Variable name of the actual date field")
    dueDateWillBeIn: Optional[int] = Field(
        None, description="Days from baseline date when interval is due"
    )
    negativeSlack: Optional[int] = Field(None, description="Days before due date allowed")
    positiveSlack: Optional[int] = Field(None, description="Days after due date allowed")
    eproGracePeriod: Optional[int] = Field(None, description="Grace days for ePRO after due date")

    @field_validator("dateCreated", "dateModified", mode="before")
    @classmethod
    def _parse_datetime(cls, value: Any) -> datetime:
        """Parse ISO or Z‑terminated datetime into a datetime object."""
        if isinstance(value, datetime):
            return value
        text = str(value)
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)


class IntervalsClient(ResourceClient):
    """Provides methods for accessing iMednet interval definitions."""

    def list_intervals(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[IntervalModel]]:
        """Retrieves a list of interval definitions for a specific study.

        GET /api/v1/edc/studies/{studyKey}/intervals
        Supports pagination, filtering, and sorting.

        Args:
            study_key: Unique identifier for the study.
            page: Zero-based page index.
            size: Number of items per page.
            sort: Sort expression (e.g., 'intervalSequence,asc').
            filter: Filter expression (e.g., 'intervalName=="Screening"').
            **kwargs: Additional query parameters.

        Returns:
            ApiResponse[List[IntervalModel]] containing intervals and pagination metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors.
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/intervals"
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
            ApiResponse[List[IntervalModel]],
            self._get(
                endpoint,
                params=params,
                response_model=ApiResponse[List[IntervalModel]],
            ),
        )
