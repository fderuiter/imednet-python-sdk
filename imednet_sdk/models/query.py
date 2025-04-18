"""Query-related data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class QueryCommentModel(BaseModel):
    """Model representing a comment or action on a query."""

    sequence: int = Field(..., description="Query comment sequence")
    user: str = Field(..., description="User performing the query action")
    annotationStatus: str = Field(..., description="User-defined query status")
    comment: str = Field(..., description="User comment applied during query action")
    closed: bool = Field(False, description="Indicates if the query was closed")
    date: datetime = Field(..., description="Date of the query comment")


class QueryModel(BaseModel):
    """Model representing a query or question related to study data."""

    studyKey: str = Field(..., description="Unique study key")
    subjectId: int = Field(..., description="Mednet Subject ID")
    subjectOid: str = Field(..., description="Client-assigned subject OID")
    annotationType: str = Field(..., description="User-defined identifier for Query Type")
    annotationId: int = Field(..., description="Unique system identifier for the Query Instance")
    type: Optional[str] = Field(None, description="System text identifier for query type/location")
    description: str = Field(..., description="Query description")
    recordId: Optional[int] = Field(None, description="Unique system identifier for Record")
    variable: Optional[str] = Field(None, description="User-defined field identifier")
    subjectKey: str = Field(..., description="Protocol-assigned subject identifier")
    dateCreated: datetime = Field(..., description="Date when the query was created")
    dateModified: datetime = Field(..., description="Date when the query was modified")
    queryComments: List[QueryCommentModel] = Field(
        ..., description="List of comments and actions on the query"
    )
