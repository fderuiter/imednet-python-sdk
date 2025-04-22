"""Pydantic models related to iMednet Queries (Annotations).

This module defines the Pydantic models `QueryCommentModel` and `QueryModel`
which represent the structure of query/annotation data retrieved from the
iMednet API, typically via the `/queries` endpoint.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class QueryCommentModel(BaseModel):
    """Represents a single comment or action taken on a query in iMednet.

    Queries typically have a history of comments and status changes, represented
    by a list of these comment models.

    Attributes:
        sequence: A sequential number identifying the order of this comment/action
                  within the query's history.
        user: The username of the user who performed the action or added the comment.
        annotationStatus: The status assigned to the query at the time of this action
                          (e.g., "Open", "Answered", "Closed").
        comment: The text of the comment added by the user.
        closed: A boolean flag indicating if this action resulted in the query being closed.
        date: The date and time when this comment/action occurred.
    """

    sequence: int = Field(..., description="Query comment sequence")
    user: str = Field(..., description="User performing the query action")
    annotationStatus: str = Field(..., description="User-defined query status")
    comment: str = Field(..., description="User comment applied during query action")
    closed: bool = Field(False, description="Indicates if the query was closed")
    date: datetime = Field(..., description="Date of the query comment")


class QueryModel(BaseModel):
    """Represents a query (or annotation) raised against data in iMednet.

    This model captures details about the query itself, its context (study, subject,
    record, variable), its status, and its history of comments/actions.

    Attributes:
        studyKey: Unique identifier for the study this query belongs to.
        subjectId: Unique numeric identifier assigned by iMednet to the subject.
        subjectOid: Client-assigned subject OID (Object Identifier).
        annotationType: User-defined identifier for the type of query (e.g., "Data Query",
                        "Monitoring Query").
        annotationId: Unique numeric identifier assigned by iMednet to this query instance.
        type: Optional system text identifier indicating the query type or location.
        description: The main text or description of the query.
        recordId: Optional unique numeric identifier for the specific record the query
                  is associated with (if applicable).
        variable: Optional name of the variable (field) the query is associated with
                  (if applicable).
        subjectKey: Protocol-assigned subject identifier (often the screen/randomization ID).
        dateCreated: The date and time when the query was initially created.
        dateModified: The date and time when the query was last modified (e.g., a comment added).
        queryComments: A list of `QueryCommentModel` objects representing the history
                       of actions and comments for this query.
    """

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
