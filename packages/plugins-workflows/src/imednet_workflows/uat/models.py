"""Pydantic models describing a complete UAT specification."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from msgspec import field as Field

from imednet.spi.models import ImednetStruct


class UATStruct(ImednetStruct, kw_only=True, omit_defaults=True, rename="camel"):
    """UAT base model with camelCase alias generation."""

    


class VariableTestStrategy(str, Enum):
    """How a variable's test value should be determined."""

    SYNTHETIC = "synthetic"
    FIXED = "fixed"
    SKIP = "skip"
    BOUNDARY = "boundary"
    CODED_ALL = "coded_all"


class RecordTestType(str, Enum):
    """What kind of record submission is being tested."""

    REGISTER_SUBJECT = "register_subject"
    UPDATE_SCHEDULED_RECORD = "update_scheduled_record"
    CREATE_NEW_RECORD = "create_new_record"


class UATVariableSpec(UATStruct, kw_only=True, omit_defaults=True):
    """Variable-level test specification."""

    variable_name: str
    variable_key: str
    variable_type: str
    form_key: str
    strategy: VariableTestStrategy = VariableTestStrategy.SYNTHETIC
    fixed_value: Any | None = None
    min_value: float | None = None
    max_value: float | None = None
    max_length: int | None = None
    coded_values: list[str] = Field(default_factory=list)
    required: bool = False
    notes: str | None = None



class UATFormSpec(UATStruct, kw_only=True, omit_defaults=True):
    """Form-level UAT test specification."""

    form_key: str
    form_name: str
    form_type: str
    test_type: RecordTestType
    interval_name: str | None = None
    subject_count: int = 1
    variables: list[UATVariableSpec] = Field(default_factory=list)
    required_variable_names: list[str] = Field(default_factory=list)
    enabled: bool = True
    notes: str | None = None




class UATSubjectSpec(UATStruct, kw_only=True, omit_defaults=True):
    """Defines synthetic test subjects to register before form submission."""

    site_name: str
    subject_count: int = 1
    subject_key_prefix: str = "UAT-TEST-"
    keyword_tag: str = "UAT"



class UATSpecification(UATStruct, kw_only=True, omit_defaults=True):
    """Root model for a complete UAT test plan."""

    spec_version: str = "1.0"
    study_key: str
    study_name: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by: str = "imednet-sdk-uat"
    subject_specs: list[UATSubjectSpec] = Field(default_factory=list)
    form_specs: list[UATFormSpec] = Field(default_factory=list)
    global_date_value: date | None = None
    global_text_length: int = 10
    forms_snapshot_count: int = 0
    variables_snapshot_count: int = 0
    intervals_snapshot_count: int = 0
    sites_snapshot_count: int = 0


    def enabled_forms(self) -> list[UATFormSpec]:
        """Return only enabled forms."""
        return [form for form in self.form_specs if form.enabled]

    def forms_by_type(self, test_type: RecordTestType) -> list[UATFormSpec]:
        """Return enabled forms matching a specific test type."""
        return [form for form in self.enabled_forms() if form.test_type == test_type]

    @classmethod
    def from_json(cls, payload: str | bytes | Path) -> UATSpecification:
        """Load a UAT specification from JSON text, bytes, or file path."""
        if isinstance(payload, Path):
            content = payload.read_text(encoding="utf-8")
        elif isinstance(payload, bytes):
            content = payload.decode("utf-8")
        else:
            content = payload

        data = json.loads(content)
        import msgspec
        return msgspec.convert(data, type=cls)


__all__ = [
    "RecordTestType",
    "UATFormSpec",
    "UATSpecification",
    "UATSubjectSpec",
    "UATVariableSpec",
    "VariableTestStrategy",
]
