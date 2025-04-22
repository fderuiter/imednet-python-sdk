"""Pydantic models related to iMednet Codings.

This module defines the Pydantic model `CodingModel` which represents the
structure of coding data retrieved from the iMednet API, typically via the
`/codings` endpoint.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CodingModel(BaseModel):
    """Represents a standardized coding applied to a data point in iMednet.

    This model captures information about a specific coding instance, linking it
    to the study, site, subject, form, record, and variable it applies to,
    as well as details about the code itself and the dictionary used.

    Attributes:
        studyKey: Unique identifier for the study.
        siteName: Name of the site where the data was collected.
        siteId: Unique numeric identifier for the site.
        subjectId: Unique numeric identifier assigned by iMednet to the subject.
        subjectKey: Protocol-assigned subject identifier (often the screen/randomization ID).
        formId: Unique numeric identifier for the form definition.
        formName: Name of the electronic Case Report Form (eCRF).
        formKey: Unique string identifier for the form definition.
        revision: The revision number of the coding metadata itself.
        recordId: Unique numeric identifier for the specific record containing the coded data.
        variable: The name of the variable (field) on the eCRF that was coded.
        value: The original value entered for the variable that was coded.
        codingId: Unique numeric identifier for this specific coding instance.
        code: The standardized code assigned (e.g., a MedDRA term code).
        codedBy: The username of the user who recorded the code.
        reason: The reason provided for applying this specific code.
        dictionaryName: The name of the coding dictionary used (e.g., "MedDRA", "WHODrug").
        dictionaryVersion: The version of the coding dictionary used.
        dateCoded: The date and time when the code was added.
    """

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
