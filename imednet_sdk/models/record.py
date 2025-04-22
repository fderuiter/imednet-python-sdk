"""Pydantic models related to iMednet Records.

This module defines the Pydantic models for representing record data retrieved
from the iMednet API (`RecordModel`, `KeywordModel`) and for structuring data
when creating new records (`RecordPostItem`).
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..exceptions import ImednetSdkException

logger = logging.getLogger(__name__)


class KeywordModel(BaseModel):
    """Represents a keyword associated with a record in iMednet.

    Keywords can be used to tag or categorize records.

    Attributes:
        keywordName: The name of the keyword.
        keywordKey: The unique key identifier for the keyword.
        keywordId: The unique numeric identifier for the keyword.
        dateAdded: The date and time when the keyword was associated with the record.
    """

    keywordName: str = Field(..., description="Name of the keyword")
    keywordKey: str = Field(..., description="Key of the keyword")
    keywordId: int = Field(..., description="Unique ID of the keyword")
    dateAdded: datetime = Field(..., description="Date the keyword was added")


class RecordModel(BaseModel):
    """Represents a single instance of an electronic Case Report Form (eCRF) record.

    This model captures the metadata and data associated with a specific record
    retrieved from the iMednet API (e.g., via the `/records` endpoint).

    Attributes:
        studyKey: Unique identifier for the study this record belongs to.
        intervalId: Unique numeric identifier for the interval (visit) this record is associated with.
        formId: Unique numeric identifier for the form definition used by this record.
        formKey: Unique string identifier for the form definition.
        siteId: Unique numeric identifier for the site associated with this record.
        recordId: Unique numeric identifier assigned by iMednet to this record.
        recordOid: Client-assigned Object Identifier (OID) for this record.
        recordType: The type of the record.
        recordStatus: The user-defined status of the record (e.g., "Complete", "In Progress").
        subjectId: Unique numeric identifier assigned by iMednet to the subject.
        subjectOid: Client-assigned Object Identifier (OID) for the subject.
        subjectKey: Protocol-assigned subject identifier (often the screen/randomization ID).
        visitId: Unique numeric identifier for the specific subject visit instance.
        parentRecordId: Optional unique numeric identifier of a parent record, if applicable.
        deleted: Boolean flag indicating if the record is marked as deleted.
        dateCreated: The date and time when the record was initially created.
        dateModified: The date and time when the record was last modified.
        keywords: An optional list of `KeywordModel` objects associated with the record.
        recordData: A dictionary containing the actual data collected in the form.
                    Keys are variable names (field names), and values are the entered data.
                    The structure of this dictionary depends on the specific form definition.
    """

    # --- Fields matching OpenAPI spec ---
    studyKey: str = Field(..., description="Unique study key")
    intervalId: int = Field(..., description="Unique ID for the interval")
    formId: int = Field(..., description="Form ID")
    formKey: str = Field(..., description="Form key")
    siteId: int = Field(..., description="Unique site ID")
    recordId: int = Field(..., description="Unique system ID for the record")
    recordOid: Optional[str] = Field(
        None, description="Client-assigned record OID"
    )  # Made Optional
    recordType: str = Field(..., description="Type of record")
    recordStatus: str = Field(..., description="User-defined record status")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: Optional[str] = Field(
        None, description="Client-assigned subject OID"
    )  # Made Optional
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    visitId: int = Field(..., description="Unique ID for the subject visit")  # Made Required
    parentRecordId: Optional[int] = Field(None, description="Parent record ID")
    deleted: bool = Field(False, description="Record deleted flag")
    dateCreated: datetime = Field(..., description="Record creation date")
    dateModified: datetime = Field(..., description="Last modification date")
    keywords: List[KeywordModel] = Field(  # Made Required (list can be empty)
        default_factory=list, description="List of keywords associated with the record"
    )
    recordData: Dict[str, Any] = Field(  # Made Required (dict can be empty)
        default_factory=dict, description="Dynamic record data containing form responses"
    )

    model_config = ConfigDict(extra="allow")

    @field_validator("dateCreated", "dateModified", mode="before")  # Updated validator fields
    @classmethod
    def parse_datetime_optional(cls, value):
        """Parse datetime strings into datetime objects, handling None."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as e:
            raise ValueError(f"Invalid datetime format: {value}") from e


class RecordPostItem(BaseModel):
    """Represents the structure of a single record item for POST requests.

    Used in the list payload when creating or updating records via the
    `POST /api/v1/edc/studies/{studyKey}/records` endpoint.

    Attributes:
        formKey: The unique string identifier for the form definition.
        data: A dictionary containing the data to be saved in the record.
              Keys are variable names (field names), and values are the data to be saved.
        siteName: Optional user-defined name of the site.
        subjectKey: Optional protocol-assigned subject identifier.
        intervalName: Optional user-defined name of the interval (visit).
        formId: Optional unique numeric identifier for the form definition.
        siteId: Optional unique numeric identifier for the site.
        subjectId: Optional unique numeric identifier for the subject.
        subjectOid: Optional client-assigned Object Identifier (OID) for the subject.
        intervalId: Optional unique numeric identifier for the interval.
        recordId: Optional unique numeric identifier for the record (used for updates).
        recordOid: Optional client-assigned Object Identifier (OID) for the record.

    Note:
        When creating records, typically `formKey`, `data`, `siteName` (or `siteId`),
        `subjectKey` (or `subjectId`), and `intervalName` (or `intervalId`) are required
        or recommended. Refer to iMednet API documentation for specific requirements.
        `recordId` or `recordOid` might be used when updating existing records via POST.
    """

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
