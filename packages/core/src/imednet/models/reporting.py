"""Reporting and analysis models for iMedNet, including CDISC-aligned datasets."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class AdverseEvent(JsonModel):
    """Canonical CDISC-aligned Adverse Event (AE) reporting model."""

    subject_key: str = Field(..., alias="subjectKey", description="Unique subject identifier")
    ae_term: str = Field(
        ..., alias="aeTerm", description="Reported term for the adverse event (AETERM)"
    )
    ae_decod: Optional[str] = Field(
        None, alias="aeDecod", description="Dictionary-derived preferred term (AEDECOD)"
    )
    ae_severity: str = Field(
        ..., alias="aeSeverity", description="Severity/intensity: MILD, MODERATE, SEVERE (AESEV)"
    )
    ae_serious: bool = Field(
        False, alias="aeSerious", description="Serious Adverse Event flag (AESER)"
    )
    ae_start_date: Optional[datetime] = Field(
        None, alias="aeStartDate", description="Start date/time of event (AESTDTC)"
    )
    ae_end_date: Optional[datetime] = Field(
        None, alias="aeEndDate", description="End date/time of event (AEENDTC)"
    )
    ae_outcome: Optional[str] = Field(
        None, alias="aeOutcome", description="Outcome of adverse event (AEOUT)"
    )
    ae_relationship: Optional[str] = Field(
        None,
        alias="aeRelationship",
        description="Causality / relationship to study drug/device (AEREL)",
    )
    ae_action_taken: Optional[str] = Field(
        None,
        alias="aeActionTaken",
        description="Action taken with study drug/device (AEACN)",
    )


class ProtocolDeviation(JsonModel):
    """Canonical CDISC-aligned Protocol Deviation (PD) reporting model."""

    subject_key: str = Field(..., alias="subjectKey", description="Unique subject identifier")
    dv_term: str = Field(..., alias="dvTerm", description="Description of the deviation (DVTERM)")
    dv_category: str = Field(
        ...,
        alias="dvCategory",
        description="Deviation category, e.g., ELIGIBILITY, CONSENT, PROCEDURE (DVCAT)",
    )
    dv_severity: str = Field(
        ...,
        alias="dvSeverity",
        description="Deviation classification: MAJOR, MINOR, CRITICAL",
    )
    dv_date: datetime = Field(..., alias="dvDate", description="Date/time of deviation (DVSTDTC)")
    dv_status: str = Field(
        "Unreviewed",
        alias="dvStatus",
        description="Triage status: Unreviewed, Approved, Escalated",
    )


class DeviceDeficiency(JsonModel):
    """Canonical CDISC-aligned Device Deficiency (DD) reporting model."""

    subject_key: str = Field(..., alias="subjectKey", description="Unique subject identifier")
    dd_term: str = Field(..., alias="ddTerm", description="Deficiency term (DDTERM)")
    dd_category: str = Field(..., alias="ddCategory", description="Category of deficiency (DDCAT)")
    dd_serious: bool = Field(
        False,
        alias="ddSerious",
        description="Serious Adverse Event relation flag (DDSPID)",
    )
    dd_date: datetime = Field(
        ..., alias="ddDate", description="Date/time of deficiency occurrence (DDSTDTC)"
    )


class SubjectLevelAnalysis(JsonModel):
    """Subject-Level Analysis Dataset (ADSL)."""

    model_config = {"extra": "allow"}
    subject_key: str = Field(..., alias="subjectKey")


class AnalysisAdverseEvent(JsonModel):
    """Analysis Adverse Event Dataset (ADAE)."""

    model_config = {"extra": "allow"}
    subject_key: str = Field(..., alias="subjectKey")


class AnalysisLabResult(JsonModel):
    """Analysis Lab Result Dataset (ADLB)."""

    model_config = {"extra": "allow"}
    subject_key: str = Field(..., alias="subjectKey")
