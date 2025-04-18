"""Coding-related data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class CodingModel(BaseModel):
    """Model representing a standardized coding of data in iMednet."""

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
    reason: str = Field(..., description="Reason for the coding")
    dictionaryName: str = Field(..., description="Name of the coding dictionary (e.g., MedDRA)")
    dictionaryVersion: str = Field(..., description="Version of the coding dictionary")
    dateCoded: datetime = Field(..., description="Date when the code was added")
