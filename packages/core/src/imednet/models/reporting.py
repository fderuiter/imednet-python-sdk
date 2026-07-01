"""Reporting and analysis models for iMedNet, including CDISC-aligned datasets."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from msgspec import field as Field

from imednet.models.json_base import JsonModel


class AdverseEvent(JsonModel, kw_only=True, omit_defaults=True):
    """Canonical CDISC-aligned Adverse Event (AE) reporting model."""

    subject_key: str = Field(name="subjectKey")
    ae_term: str = Field(name="aeTerm")
    ae_decod: Optional[str] = Field(default=None, name="aeDecod")
    ae_severity: str = Field(name="aeSeverity")
    ae_serious: bool = Field(default=False, name="aeSerious")
    ae_start_date: Optional[datetime] = Field(default=None, name="aeStartDate")
    ae_end_date: Optional[datetime] = Field(default=None, name="aeEndDate")
    ae_outcome: Optional[str] = Field(default=None, name="aeOutcome")
    ae_relationship: Optional[str] = Field(default=None, name="aeRelationship")
    ae_action_taken: Optional[str] = Field(default=None, name="aeActionTaken")


class ProtocolDeviation(JsonModel, kw_only=True, omit_defaults=True):
    """Canonical CDISC-aligned Protocol Deviation (PD) reporting model."""

    subject_key: str = Field(name="subjectKey")
    dv_term: str = Field(name="dvTerm")
    dv_category: str = Field(name="dvCategory")
    dv_severity: str = Field(name="dvSeverity")
    dv_date: datetime = Field(name="dvDate")
    dv_status: str = Field(default="Unreviewed", name="dvStatus")


class DeviceDeficiency(JsonModel, kw_only=True, omit_defaults=True):
    """Canonical CDISC-aligned Device Deficiency (DD) reporting model."""

    subject_key: str = Field(name="subjectKey")
    dd_term: str = Field(name="ddTerm")
    dd_category: str = Field(name="ddCategory")
    dd_serious: bool = Field(default=False, name="ddSerious")
    dd_date: datetime = Field(name="ddDate")


class SubjectLevelAnalysis(JsonModel, kw_only=True, omit_defaults=True):
    """Subject-Level Analysis Dataset (ADSL)."""

    model_config = {"extra": "allow"}
    subject_key: str 


class AnalysisAdverseEvent(JsonModel, kw_only=True, omit_defaults=True):
    """Analysis Adverse Event Dataset (ADAE)."""

    model_config = {"extra": "allow"}
    subject_key: str 


class AnalysisLabResult(JsonModel, kw_only=True, omit_defaults=True):
    """Analysis Lab Result Dataset (ADLB)."""

    model_config = {"extra": "allow"}
    subject_key: str 
