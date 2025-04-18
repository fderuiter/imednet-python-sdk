"""Variable-related data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class VariableModel(BaseModel):
    """Model representing a data point on an electronic clinical case report form (eCRF)."""

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
    variableOid: str = Field(..., description="Client-assigned Variable OID")
    deleted: bool = Field(False, description="Flag indicating if the variable is deleted")
    formKey: str = Field(..., description="Form key")
    formName: str = Field(..., description="Name of the eCRF")
    label: str = Field(..., description="User-defined field label")
    blinded: bool = Field(False, description="Flag indicating if the variable is blinded")
