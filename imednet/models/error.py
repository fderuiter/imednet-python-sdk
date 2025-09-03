from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .json_base import JsonModel


class ApiErrorDetail(JsonModel):
    """Represents the detailed structure of an error response from the API."""

    type: Optional[str] = Field(None, description="A URI that identifies the problem type.")
    title: Optional[str] = Field(
        None, description="A short, human-readable summary of the problem."
    )
    status: Optional[int] = Field(None, description="The HTTP status code.")
    detail: Optional[str] = Field(
        None,
        description="A human-readable explanation specific to this occurrence of the problem.",
    )
    instance: Optional[str] = Field(
        None, description="A URI that identifies the specific occurrence of the problem."
    )
    errors: Optional[List[str]] = Field(None, description="A list of validation errors.")
