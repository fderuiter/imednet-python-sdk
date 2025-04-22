"""Pydantic models related to iMednet Record Revisions (Audit Trail).

This module defines the Pydantic model `RecordRevisionModel` which represents
the structure of record audit trail data retrieved from the iMednet API,
typically via the `/recordRevisions` endpoint.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RecordRevisionModel(BaseModel):
    """Represents a single entry in the audit trail (revision history) of a record.

    Each instance captures a specific state or change made to a record, including
    who made the change, when, and potentially why.

    Attributes:
        studyKey: Unique identifier for the study this record revision belongs to.
        recordRevisionId: Unique numeric identifier assigned by iMednet to this specific revision.
        recordId: Unique numeric identifier for the record that was revised.
        recordOid: Client-assigned Object Identifier (OID) for the record.
        recordRevision: The revision number specific to the record's overall state.
        dataRevision: The revision number specific to changes in the record's data.
        recordStatus: The user-defined status of the record at the time of this revision.
        subjectId: Unique numeric identifier assigned by iMednet to the subject.
        subjectOid: Client-assigned Object Identifier (OID) for the subject.
        subjectKey: Protocol-assigned subject identifier (often the screen/randomization ID).
        siteId: Unique numeric identifier for the site associated with the record.
        formKey: Unique string identifier for the form definition used by the record.
        intervalId: Unique numeric identifier for the interval (visit) associated with the record.
        role: The role of the user who saved this record revision.
        user: The username of the user who saved this record revision.
        reasonForChange: Optional reason provided by the user for the change made in this revision.
        deleted: Boolean flag indicating if this revision represents the deletion of the record.
        dateCreated: The date and time when this specific record revision was created.
    """

    studyKey: str = Field(..., description="Unique study key for the given study")
    recordRevisionId: int = Field(
        ..., description="Unique system identifier for the record revision"
    )
    recordId: int = Field(..., description="Unique system identifier for the related record")
    recordOid: str = Field(..., description="Client-assigned record OID")
    recordRevision: int = Field(..., description="Record revision number")
    dataRevision: int = Field(..., description="Data revision number")
    recordStatus: str = Field(..., description="User-defined record status")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: str = Field(..., description="Client-assigned subject OID")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    siteId: int = Field(..., description="Unique system identifier for the related site")
    formKey: str = Field(..., description="Form key")
    intervalId: int = Field(..., description="Unique system identifier for the interval")
    role: str = Field(..., description="Role of the user who saved the record revision")
    user: str = Field(..., description="Username of the user who saved the record revision")
    reasonForChange: Optional[str] = Field(
        None, description="Reason for the change made in the record revision"
    )
    deleted: bool = Field(False, description="Indicates whether the record was deleted")
    dateCreated: datetime = Field(..., description="Date when the record revision was created")
