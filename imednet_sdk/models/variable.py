"""Pydantic models related to iMednet Variables (Form Fields).

This module defines the Pydantic model `VariableModel` which represents the
structure of variable definition data retrieved from the iMednet API,
typically via the `/variables` endpoint. Variables define the individual
data fields within a form.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VariableModel(BaseModel):
    """Represents the definition of a variable (field) on an eCRF in iMednet.

    This model captures metadata about a specific data field within a form,
    including its identifiers, type, name, sequence, and other attributes.

    Attributes:
        studyKey: Unique identifier for the study this variable belongs to.
        variableId: Unique numeric identifier assigned by iMednet to this variable definition.
        variableType: The type of the variable (e.g., "radioField", "textField", "dateField").
                      Determines the kind of data expected and how it's displayed.
        variableName: The unique name (often code) assigned to the variable within the form.
                      Used as the key in the `recordData` dictionary.
        sequence: User-defined sequence number for ordering variables within the form.
        revision: The revision number of the variable definition metadata.
        disabled: Boolean flag indicating if the variable is currently disabled on the form.
        dateCreated: The date and time when the variable definition was initially created.
        dateModified: The date and time when the variable definition was last modified.
        formId: Unique numeric identifier for the form definition this variable belongs to.
        variableOid: Client-assigned Object Identifier (OID) for this variable definition.
        deleted: Boolean flag indicating if the variable definition is marked as deleted.
        formKey: Unique string identifier for the form definition this variable belongs to.
        formName: The display name of the form this variable belongs to.
        label: The user-visible label or question text associated with the variable on the form.
        blinded: Boolean flag indicating if the variable's data should be blinded.
    """

    studyKey: str = Field(..., description="Unique Study Key")
    variableId: int = Field(..., description="Mednet Variable ID")
    variableType: str = Field(..., description="Type of the variable (e.g., RADIO, TEXT)")
    variableName: str = Field(..., description="Name of the variable on the eCRF")
    sequence: int = Field(..., description="User-defined sequence of the variable")
    revision: int = Field(..., description="Number of modifications to the form metadata")
    disabled: bool = Field(False, description="Flag indicating if the variable is disabled")
    dateCreated: datetime = Field(..., description="Creation date of the variable")
    dateModified: datetime = Field(..., description="Last modification date of the variable")
    formId: int = Field(..., description="Mednet Form ID")
    variableOid: Optional[str] = Field(None, description="Client-assigned Variable OID")
    deleted: bool = Field(False, description="Flag indicating if the variable is deleted")
    formKey: str = Field(..., description="Form key")
    formName: str = Field(..., description="Name of the eCRF")
    label: str = Field(..., description="User-defined field label")
    blinded: bool = Field(False, description="Flag indicating if the variable is blinded")
