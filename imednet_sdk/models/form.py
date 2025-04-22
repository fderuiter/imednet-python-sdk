"""Pydantic models related to iMednet Forms (eCRFs).

This module defines the Pydantic model `FormModel` which represents the
structure of form definition data retrieved from the iMednet API, typically
via the `/forms` endpoint.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class FormModel(BaseModel):
    """Represents the definition of an electronic Case Report Form (eCRF) in iMednet.

    This model captures metadata about a form, including its identifiers, name,
    type, revision history, and various configuration settings.

    Attributes:
        studyKey: Unique identifier for the study this form belongs to.

        formId: Unique numeric identifier assigned by iMednet to the form definition.

        formKey: Unique string identifier for the form definition.

        formName: The display name of the eCRF.

        formType: The type of the eCRF (e.g., "Subject", "Site", "Common").

        revision: The revision number of the form definition metadata.

        embeddedLog: Boolean flag indicating if the form uses an embedded log.

        enforceOwnership: Boolean flag indicating if ownership is enforced for records
                          created from this form.

        userAgreement: Boolean flag indicating if a user agreement is associated with
                       this form.

        subjectRecordReport: Boolean flag related to subject record reporting.

        unscheduledVisit: Boolean flag indicating if this form can be used in
                          unscheduled visits.

        otherForms: Boolean flag indicating if this form is included in "Other Forms".

        eproForm: Boolean flag indicating if this is an ePRO (electronic Patient
                  Reported Outcome) form.

        allowCopy: Boolean flag indicating if records created from this form can be copied.

        disabled: Boolean flag indicating if the form is currently disabled (soft delete).

        dateCreated: The date and time when the form definition was initially created.

        dateModified: The date and time when the form definition was last modified.
    """

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
