"""Tests for test_discovery."""

from unittest.mock import Mock

import pytest

from imednet.discovery import (
    ELIGIBLE_SITE_STATUSES,
    ELIGIBLE_SUBJECT_STATUSES,
    NoLiveDataError,
    discover_form_key,
    discover_interval_name,
    discover_site_name,
    discover_subject_key,
    is_site_eligible,
    is_subject_eligible,
)
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.sites import Site
from imednet.models.subjects import Subject

# ---------------------------------------------------------------------------
# is_site_eligible
# ---------------------------------------------------------------------------


def test_is_site_eligible_accepts_enrollment_open() -> None:
    """Test test_is_site_eligible_accepts_enrollment_open behavior."""
    assert is_site_eligible("ENROLLMENT_OPEN") is True


def test_is_site_eligible_accepts_active_case_insensitive() -> None:
    """Test test_is_site_eligible_accepts_active_case_insensitive behavior."""
    assert is_site_eligible("Active") is True
    assert is_site_eligible("ACTIVE") is True


def test_is_site_eligible_rejects_read_only() -> None:
    """Test test_is_site_eligible_rejects_read_only behavior."""
    assert is_site_eligible("READ_ONLY") is False


def test_is_site_eligible_rejects_closed() -> None:
    """Test test_is_site_eligible_rejects_closed behavior."""
    assert is_site_eligible("Closed") is False


def test_eligible_site_statuses_contains_expected_values() -> None:
    """Test test_eligible_site_statuses_contains_expected_values behavior."""
    assert "enrollment_open" in ELIGIBLE_SITE_STATUSES
    assert "active" in ELIGIBLE_SITE_STATUSES


# ---------------------------------------------------------------------------
# is_subject_eligible
# ---------------------------------------------------------------------------


def test_is_subject_eligible_accepts_registered() -> None:
    """Test test_is_subject_eligible_accepts_registered behavior."""
    assert is_subject_eligible("Registered") is True


def test_is_subject_eligible_accepts_baseline() -> None:
    """Test test_is_subject_eligible_accepts_baseline behavior."""
    assert is_subject_eligible("Baseline") is True


def test_is_subject_eligible_accepts_enrolled() -> None:
    """Test test_is_subject_eligible_accepts_enrolled behavior."""
    assert is_subject_eligible("Enrolled") is True


def test_is_subject_eligible_accepts_active_case_insensitive() -> None:
    """Test test_is_subject_eligible_accepts_active_case_insensitive behavior."""
    assert is_subject_eligible("Active") is True
    assert is_subject_eligible("ACTIVE") is True


def test_is_subject_eligible_rejects_closed() -> None:
    """Test test_is_subject_eligible_rejects_closed behavior."""
    assert is_subject_eligible("Closed") is False


def test_eligible_subject_statuses_contains_expected_values() -> None:
    """Test test_eligible_subject_statuses_contains_expected_values behavior."""
    assert "registered" in ELIGIBLE_SUBJECT_STATUSES
    assert "baseline" in ELIGIBLE_SUBJECT_STATUSES
    assert "enrolled" in ELIGIBLE_SUBJECT_STATUSES
    assert "active" in ELIGIBLE_SUBJECT_STATUSES


# ---------------------------------------------------------------------------
# discover_form_key
# ---------------------------------------------------------------------------


def test_discover_form_key_chooses_subject_form() -> None:
    """Test test_discover_form_key_chooses_subject_form behavior."""
    sdk = Mock()
    sdk.forms.list.return_value = [
        Form(study_key="S", form_key="SS", subject_record_report=False),
        Form(study_key="S", form_key="F1", subject_record_report=True, disabled=True),
        Form(study_key="S", form_key="F2", subject_record_report=True, disabled=False),
    ]
    sdk.variables.list.return_value = [Mock()]

    assert discover_form_key(sdk, "S") == "F2"


def test_discover_form_key_raises_when_no_valid_forms() -> None:
    """Test test_discover_form_key_raises_when_no_valid_forms behavior."""
    sdk = Mock()
    sdk.forms.list.return_value = [Form(study_key="S", form_key="SS", subject_record_report=False)]
    sdk.variables.list.return_value = [Mock()]

    with pytest.raises(NoLiveDataError):
        discover_form_key(sdk, "S")


# ---------------------------------------------------------------------------
# discover_site_name
# ---------------------------------------------------------------------------


def test_discover_site_name_returns_active_site() -> None:
    """Test test_discover_site_name_returns_active_site behavior."""
    sdk = Mock()
    sdk.sites.list.return_value = [
        Site(study_key="S", site_name="Closed", site_enrollment_status="Closed"),
        Site(study_key="S", site_name="Open", site_enrollment_status="Active"),
    ]

    assert discover_site_name(sdk, "S") == "Open"
    sdk.sites.list.assert_called_once_with(study_key="S")


def test_discover_site_name_returns_enrollment_open_site() -> None:
    """Sites with ENROLLMENT_OPEN status should be considered eligible."""
    sdk = Mock()
    sdk.sites.list.return_value = [
        Site(study_key="S", site_name="ReadOnly", site_enrollment_status="READ_ONLY"),
        Site(study_key="S", site_name="EnrollOpen", site_enrollment_status="ENROLLMENT_OPEN"),
    ]

    assert discover_site_name(sdk, "S") == "EnrollOpen"


def test_discover_site_name_raises_when_no_active() -> None:
    """Test test_discover_site_name_raises_when_no_active behavior."""
    sdk = Mock()
    sdk.sites.list.return_value = [
        Site(study_key="S", site_name="X", site_enrollment_status="Closed")
    ]

    with pytest.raises(NoLiveDataError):
        discover_site_name(sdk, "S")


def test_discover_site_name_error_includes_encountered_statuses() -> None:
    """NoLiveDataError message should include the statuses that were found."""
    sdk = Mock()
    sdk.sites.list.return_value = [
        Site(study_key="S", site_name="A", site_enrollment_status="READ_ONLY"),
        Site(study_key="S", site_name="B", site_enrollment_status="READ_ONLY"),
    ]

    with pytest.raises(NoLiveDataError, match="READ_ONLY"):
        discover_site_name(sdk, "S")


def test_discover_site_name_raises_when_no_sites() -> None:
    """Test test_discover_site_name_raises_when_no_sites behavior."""
    sdk = Mock()
    sdk.sites.list.return_value = []

    with pytest.raises(NoLiveDataError):
        discover_site_name(sdk, "S")


# ---------------------------------------------------------------------------
# discover_subject_key
# ---------------------------------------------------------------------------


def test_discover_subject_key_returns_active_subject() -> None:
    """Test test_discover_subject_key_returns_active_subject behavior."""
    sdk = Mock()
    sdk.subjects.list.return_value = [
        Subject(study_key="S", subject_key="S1", subject_status="Closed"),
        Subject(study_key="S", subject_key="S2", subject_status="Active"),
    ]

    assert discover_subject_key(sdk, "S") == "S2"
    sdk.subjects.list.assert_called_once_with(study_key="S")


def test_discover_subject_key_returns_registered_subject() -> None:
    """Subjects with Registered status should be considered eligible."""
    sdk = Mock()
    sdk.subjects.list.return_value = [
        Subject(study_key="S", subject_key="S1", subject_status="Registered"),
    ]

    assert discover_subject_key(sdk, "S") == "S1"


def test_discover_subject_key_returns_baseline_subject() -> None:
    """Subjects with Baseline status should be considered eligible."""
    sdk = Mock()
    sdk.subjects.list.return_value = [
        Subject(study_key="S", subject_key="S1", subject_status="Baseline"),
    ]

    assert discover_subject_key(sdk, "S") == "S1"


def test_discover_subject_key_returns_enrolled_subject() -> None:
    """Subjects with Enrolled status should be considered eligible."""
    sdk = Mock()
    sdk.subjects.list.return_value = [
        Subject(study_key="S", subject_key="S1", subject_status="Enrolled"),
    ]

    assert discover_subject_key(sdk, "S") == "S1"


def test_discover_subject_key_raises_when_no_active() -> None:
    """Test test_discover_subject_key_raises_when_no_active behavior."""
    sdk = Mock()
    sdk.subjects.list.return_value = [
        Subject(study_key="S", subject_key="S1", subject_status="Closed")
    ]

    with pytest.raises(NoLiveDataError):
        discover_subject_key(sdk, "S")


def test_discover_subject_key_error_includes_encountered_statuses() -> None:
    """NoLiveDataError message should include the statuses that were found."""
    sdk = Mock()
    sdk.subjects.list.return_value = [
        Subject(study_key="S", subject_key="S1", subject_status="Closed"),
        Subject(study_key="S", subject_key="S2", subject_status="Withdrawn"),
    ]

    with pytest.raises(NoLiveDataError, match="Closed|Withdrawn"):
        discover_subject_key(sdk, "S")


def test_discover_subject_key_raises_when_no_subjects() -> None:
    """Test test_discover_subject_key_raises_when_no_subjects behavior."""
    sdk = Mock()
    sdk.subjects.list.return_value = []

    with pytest.raises(NoLiveDataError):
        discover_subject_key(sdk, "S")


# ---------------------------------------------------------------------------
# discover_interval_name
# ---------------------------------------------------------------------------


def test_discover_interval_name_returns_active_interval() -> None:
    """Test test_discover_interval_name_returns_active_interval behavior."""
    sdk = Mock()
    sdk.intervals.list.return_value = [
        Interval(study_key="S", interval_name="I1", disabled=True),
        Interval(study_key="S", interval_name="I2", disabled=False),
    ]

    assert discover_interval_name(sdk, "S") == "I2"
    sdk.intervals.list.assert_called_once_with(study_key="S")


def test_discover_interval_name_raises_when_all_disabled() -> None:
    """Test test_discover_interval_name_raises_when_all_disabled behavior."""
    sdk = Mock()
    sdk.intervals.list.return_value = [Interval(study_key="S", interval_name="I1", disabled=True)]

    with pytest.raises(NoLiveDataError):
        discover_interval_name(sdk, "S")
