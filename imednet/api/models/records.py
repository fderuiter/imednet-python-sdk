from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from pydantic import Field, RootModel

from .json_base import JsonModel


class Keyword(JsonModel):
    """Represents a keyword or tag associated with a record."""

    keyword_name: str = Field("", alias="keywordName", description="The name of the keyword.")
    keyword_key: str = Field("", alias="keywordKey", description="The key of the keyword.")
    keyword_id: int = Field(0, alias="keywordId", description="The ID of the keyword.")
    date_added: datetime = Field(
        default_factory=datetime.now,
        alias="dateAdded",
        description="The date the keyword was added.",
    )


class Record(JsonModel):
    """Represents a single data record for a subject, form, and visit."""

    study_key: str = Field("", alias="studyKey", description="The key of the study.")
    interval_id: int = Field(0, alias="intervalId", description="The ID of the interval.")
    form_id: int = Field(0, alias="formId", description="The ID of the form.")
    form_key: str = Field("", alias="formKey", description="The key of the form.")
    site_id: int = Field(0, alias="siteId", description="The ID of the site.")
    record_id: int = Field(0, alias="recordId", description="The ID of the record.")
    record_oid: str = Field("", alias="recordOid", description="The OID of the record.")
    record_type: str = Field("", alias="recordType", description="The type of the record.")
    record_status: str = Field("", alias="recordStatus", description="The status of the record.")
    deleted: bool = Field(False, alias="deleted", description="Indicates if the record is deleted.")
    date_created: datetime = Field(
        default_factory=datetime.now,
        alias="dateCreated",
        description="The date the record was created.",
    )
    date_modified: datetime = Field(
        default_factory=datetime.now,
        alias="dateModified",
        description="The date the record was last modified.",
    )
    subject_id: int = Field(0, alias="subjectId", description="The ID of the subject.")
    subject_oid: str = Field("", alias="subjectOid", description="The OID of the subject.")
    subject_key: str = Field("", alias="subjectKey", description="The key of the subject.")
    visit_id: int = Field(0, alias="visitId", description="The ID of the visit.")
    parent_record_id: int = Field(
        0, alias="parentRecordId", description="The ID of the parent record, if any."
    )
    keywords: List[Keyword] = Field(
        default_factory=list, alias="keywords", description="A list of keywords for the record."
    )
    record_data: Dict[str, Any] = Field(
        default_factory=dict, alias="recordData", description="The actual data of the record."
    )


class RecordJobResponse(JsonModel):
    """Represents the response from a job that operates on records."""

    job_id: str = Field("", alias="jobId", description="The ID of the job.")
    batch_id: str = Field("", alias="batchId", description="The batch ID of the job.")
    state: str = Field("", alias="state", description="The current state of the job.")


class RecordData(RootModel[Dict[str, Any]]):
    """Represents the flexible data portion of a record.

    This is a `RootModel` that wraps a dictionary, allowing for arbitrary
    key-value pairs representing the form data.
    """


class BaseRecordRequest(JsonModel):
    """A base model for requests that create or update records."""

    form_key: str = Field("", alias="formKey", description="The key of the form for the record.")
    data: RecordData = Field(
        default_factory=lambda: RecordData({}), alias="data", description="The data for the record."
    )


class RegisterSubjectRequest(BaseRecordRequest):
    """Represents a request to register a new subject."""

    site_name: str = Field(
        "", alias="siteName", description="Name of the site where the subject is enrolled"
    )
    subject_key: str = Field(
        "", alias="subjectKey", description="Unique identifier for the subject"
    )


class UpdateScheduledRecordRequest(BaseRecordRequest):
    """Represents a request to update a record for a scheduled visit."""

    subject_key: str = Field("", alias="subjectKey", description="The key of the subject.")
    interval_name: str = Field(
        "", alias="intervalName", description="The name of the interval for the visit."
    )


class CreateNewRecordRequest(BaseRecordRequest):
    """Represents a request to create a new, unscheduled record."""

    subject_key: str = Field("", alias="subjectKey", description="The key of the subject.")
