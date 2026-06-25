"""Test Discovery module."""

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
    """Test the test is site eligible accepts enrollment open functionality."""
    assert is_site_eligible("ENROLLMENT_OPEN") is True


def test_is_site_eligible_accepts_active_case_insensitive() -> None:
    """Test the test is site eligible accepts active case insensitive functionality."""
    assert is_site_eligible("Active") is True
    assert is_site_eligible("ACTIVE") is True


def test_is_site_eligible_rejects_read_only() -> None:
    """Test the test is site eligible rejects read only functionality."""
    assert is_site_eligible("READ_ONLY") is False


def test_is_site_eligible_rejects_closed() -> None:
    """Test the test is site eligible rejects closed functionality."""
    assert is_site_eligible("Closed") is False


def test_eligible_site_statuses_contains_expected_values() -> None:
    """Test the test eligible site statuses contains expected values functionality."""
    assert "enrollment_open" in ELIGIBLE_SITE_STATUSES
    assert "active" in ELIGIBLE_SITE_STATUSES


# ---------------------------------------------------------------------------
# is_subject_eligible
# ---------------------------------------------------------------------------


def test_is_subject_eligible_accepts_registered() -> None:
    """Test the test is subject eligible accepts registered functionality."""
    assert is_subject_eligible("Registered") is True


def test_is_subject_eligible_accepts_baseline() -> None:
    """Test the test is subject eligible accepts baseline functionality."""
    assert is_subject_eligible("Baseline") is True


def test_is_subject_eligible_accepts_enrolled() -> None:
    """Test the test is subject eligible accepts enrolled functionality."""
    assert is_subject_eligible("Enrolled") is True


def test_is_subject_eligible_accepts_active_case_insensitive() -> None:
    """Test the test is subject eligible accepts active case insensitive functionality."""
    assert is_subject_eligible("Active") is True
    assert is_subject_eligible("ACTIVE") is True


def test_is_subject_eligible_rejects_closed() -> None:
    """Test the test is subject eligible rejects closed functionality."""
    assert is_subject_eligible("Closed") is False


def test_eligible_subject_statuses_contains_expected_values() -> None:
    """Test the test eligible subject statuses contains expected values functionality."""
    assert "registered" in ELIGIBLE_SUBJECT_STATUSES
    assert "baseline" in ELIGIBLE_SUBJECT_STATUSES
    assert "enrolled" in ELIGIBLE_SUBJECT_STATUSES
    assert "active" in ELIGIBLE_SUBJECT_STATUSES


# ---------------------------------------------------------------------------
# discover_form_key
# ---------------------------------------------------------------------------


def test_discover_form_key_chooses_subject_form() -> None:
    """Test the test discover form key chooses subject form functionality."""
    sdk = Mock()
    sdk.forms.list.return_value = [
        Form(study_key="S", form_key="SS", subject_record_report=False),
        Form(study_key="S", form_key="F1", subject_record_report=True, disabled=True),
        Form(study_key="S", form_key="F2", subject_record_report=True, disabled=False),
    ]
    sdk.variables.list.return_value = [Mock()]

    assert discover_form_key(sdk, "S") == "F2"


def test_discover_form_key_raises_when_no_valid_forms() -> None:
    """Test the test discover form key raises when no valid forms functionality."""
    sdk = Mock()
    sdk.forms.list.return_value = [Form(study_key="S", form_key="SS", subject_record_report=False)]
    sdk.variables.list.return_value = [Mock()]

    with pytest.raises(NoLiveDataError):
        discover_form_key(sdk, "S")


# ---------------------------------------------------------------------------
# discover_site_name
# ---------------------------------------------------------------------------


def test_discover_site_name_returns_active_site() -> None:
    """Test the test discover site name returns active site functionality."""
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
    """Test the test discover site name raises when no active functionality."""
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
    """Test the test discover site name raises when no sites functionality."""
    sdk = Mock()
    sdk.sites.list.return_value = []

    with pytest.raises(NoLiveDataError):
        discover_site_name(sdk, "S")


# ---------------------------------------------------------------------------
# discover_subject_key
# ---------------------------------------------------------------------------


def test_discover_subject_key_returns_active_subject() -> None:
    """Test the test discover subject key returns active subject functionality."""
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
    """Test the test discover subject key raises when no active functionality."""
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
    """Test the test discover subject key raises when no subjects functionality."""
    sdk = Mock()
    sdk.subjects.list.return_value = []

    with pytest.raises(NoLiveDataError):
        discover_subject_key(sdk, "S")


# ---------------------------------------------------------------------------
# discover_interval_name
# ---------------------------------------------------------------------------


def test_discover_interval_name_returns_active_interval() -> None:
    """Test the test discover interval name returns active interval functionality."""
    sdk = Mock()
    sdk.intervals.list.return_value = [
        Interval(study_key="S", interval_name="I1", disabled=True),
        Interval(study_key="S", interval_name="I2", disabled=False),
    ]

    assert discover_interval_name(sdk, "S") == "I2"
    sdk.intervals.list.assert_called_once_with(study_key="S")


def test_discover_interval_name_raises_when_all_disabled() -> None:
    """Test the test discover interval name raises when all disabled functionality."""
    sdk = Mock()
    sdk.intervals.list.return_value = [Interval(study_key="S", interval_name="I1", disabled=True)]

    with pytest.raises(NoLiveDataError):
        discover_interval_name(sdk, "S")
