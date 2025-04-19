"""Record-related data models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .subject import KeywordModel


class RecordModel(BaseModel):
    """Model representing a single instance of an electronic case report form (eCRF)."""

    studyKey: str = Field(..., description="Unique study key")
    intervalId: int = Field(..., description="Unique ID for the interval")
    formId: int = Field(..., description="Form ID")
    formKey: str = Field(..., description="Form key")
    siteId: int = Field(..., description="Unique site ID")
    recordId: int = Field(..., description="Unique system ID for the record")
    recordOid: str = Field(..., description="Client-assigned record OID")
    recordType: str = Field(..., description="Type of record")
    recordStatus: str = Field(..., description="User-defined record status")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: str = Field(..., description="Client-assigned subject OID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    visitId: Optional[int] = Field(None, description="Unique ID for the subject visit")
    parentRecordId: Optional[int] = Field(None, description="Parent record ID")
    deleted: bool = Field(False, description="Record deleted flag")
    dateCreated: datetime = Field(..., description="Record creation date")
    dateModified: datetime = Field(..., description="Last modification date")
    keywords: Optional[List[KeywordModel]] = Field(
        None, description="List of keywords associated with the record"
    )
    recordData: Dict[str, Any] = Field(
        default_factory=dict, description="Dynamic record data containing form responses"
    )


class RecordCreateRequest(BaseModel):
    """Model for creating a new record."""

    # Note: This will be populated with fields based on the POST /records requirements
    formKey: str = Field(..., description="User-defined form key")
    formId: Optional[int] = Field(None, description="System-generated form ID")
    # Add other required fields for record creation


class RecordPostItem(BaseModel):
    """Model representing a single item in the POST request body for creating/updating records."""

    formKey: str = Field(..., description="User-defined form key")
    data: Dict[str, Any] = Field(
        ..., description="Data for the specific record (field keys and values)"
    )

    siteName: Optional[str] = Field(None, description="User-defined site name")
    subjectKey: Optional[str] = Field(None, description="Protocol-assigned subject identifier")
    intervalName: Optional[str] = Field(None, description="User-defined interval name")

    formId: Optional[int] = Field(None, description="System-generated form ID")
    siteId: Optional[int] = Field(None, description="System-generated site ID")
    subjectId: Optional[int] = Field(None, description="System-generated subject ID")
    subjectOid: Optional[str] = Field(None, description="Client-assigned subject OID")
    intervalId: Optional[int] = Field(None, description="System-generated interval ID")
    recordId: Optional[int] = Field(None, description="System-generated record ID")
    recordOid: Optional[str] = Field(None, description="Client-assigned record OID")
