"""Form-related data models."""

from datetime import datetime

from pydantic import BaseModel, Field


class FormModel(BaseModel):
    """Model representing an electronic clinical case report form (eCRF)."""

    studyKey: str = Field(..., description="Unique study key")
    formId: int = Field(..., description="Mednet Form ID")
    formKey: str = Field(..., description="Form key")
    formName: str = Field(..., description="Name of the eCRF")
    formType: str = Field(..., description="eCRF Type (e.g., Subject, Site)")
    revision: int = Field(..., description="Number of modifications to the form metadata")
    embeddedLog: bool = Field(
        False, description="Embedded Log checkbox value on the form attributes"
    )
    enforceOwnership: bool = Field(
        False, description="Enforce Ownership checkbox value on the form attributes"
    )
    userAgreement: bool = Field(
        False, description="User Agreement checkbox value on the form attributes"
    )
    subjectRecordReport: bool = Field(
        False, description="Subject Record Report checkbox value on the form attributes"
    )
    unscheduledVisit: bool = Field(
        False, description="Include in Unscheduled Visits checkbox value"
    )
    otherForms: bool = Field(False, description="Include in Other Forms checkbox value")
    eproForm: bool = Field(False, description="Is ePRO checkbox value on the form attributes")
    allowCopy: bool = Field(True, description="Allow Copy checkbox value on the form attributes")
    disabled: bool = Field(False, description="Form is soft delete status")
    dateCreated: datetime = Field(..., description="Date when the form was created")
    dateModified: datetime = Field(..., description="Last modification date of the form")
