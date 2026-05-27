from unittest.mock import MagicMock

import pytest

from imednet.discovery import (
    NoLiveDataError,
    discover_form_key,
    discover_interval_name,
    discover_site_name,
    discover_study_key,
    discover_subject_key,
)


def test_discover_study_key_returns_first() -> None:
    sdk = MagicMock()
    sdk.studies.list.return_value = [
        MagicMock(study_key="S1"),
        MagicMock(study_key="S2"),
    ]

    assert discover_study_key(sdk) == "S1"
    sdk.studies.list.assert_called_once_with()


def test_discover_study_key_raises_when_empty() -> None:
    sdk = MagicMock()
    sdk.studies.list.return_value = []

    with pytest.raises(NoLiveDataError):
        discover_study_key(sdk)


def test_discover_form_key_returns_first_matching() -> None:
    sdk = MagicMock()
    sdk.forms.list.return_value = [
        MagicMock(subject_record_report=False),
        MagicMock(form_key="F1", subject_record_report=True, disabled=False),
        MagicMock(form_key="F2", subject_record_report=True, disabled=False),
    ]

    assert discover_form_key(sdk, "S") == "F1"
    sdk.forms.list.assert_called_once_with(study_key="S")


def test_discover_form_key_raises_when_empty() -> None:
    sdk = MagicMock()
    sdk.forms.list.return_value = []

    with pytest.raises(NoLiveDataError):
        discover_form_key(sdk, "S")


def test_discover_site_name_returns_first_active() -> None:
    sdk = MagicMock()
    sdk.sites.list.return_value = [
        MagicMock(site_enrollment_status="Closed"),
        MagicMock(site_name="Open", site_enrollment_status="Active"),
    ]

    assert discover_site_name(sdk, "S") == "Open"
    sdk.sites.list.assert_called_once_with(study_key="S")


def test_discover_site_name_raises_when_empty() -> None:
    sdk = MagicMock()
    sdk.sites.list.return_value = []

    with pytest.raises(NoLiveDataError):
        discover_site_name(sdk, "S")


def test_discover_subject_key_returns_first_active() -> None:
    sdk = MagicMock()
    sdk.subjects.list.return_value = [
        MagicMock(subject_status="Closed"),
        MagicMock(subject_key="S2", subject_status="Active"),
    ]

    assert discover_subject_key(sdk, "S") == "S2"
    sdk.subjects.list.assert_called_once_with(study_key="S")


def test_discover_subject_key_raises_when_empty() -> None:
    sdk = MagicMock()
    sdk.subjects.list.return_value = []

    with pytest.raises(NoLiveDataError):
        discover_subject_key(sdk, "S")


def test_discover_interval_name_returns_first_enabled() -> None:
    sdk = MagicMock()
    sdk.intervals.list.return_value = [
        MagicMock(disabled=True),
        MagicMock(interval_name="I2", disabled=False),
    ]

    assert discover_interval_name(sdk, "S") == "I2"
    sdk.intervals.list.assert_called_once_with(study_key="S")


def test_discover_interval_name_raises_when_empty() -> None:
    sdk = MagicMock()
    sdk.intervals.list.return_value = []

    with pytest.raises(NoLiveDataError):
        discover_interval_name(sdk, "S")


def test_discover_site_name_case_insensitive() -> None:
    """Status matching must be case-insensitive per the live-test charter."""
    sdk = MagicMock()
    sdk.sites.list.return_value = [
        MagicMock(site_name="Lower", site_enrollment_status="active"),
        MagicMock(site_name="Upper", site_enrollment_status="ACTIVE"),
        MagicMock(site_name="Mixed", site_enrollment_status="Active"),
    ]

    assert discover_site_name(sdk, "S") == "Lower"


def test_discover_subject_key_case_insensitive() -> None:
    """Status matching must be case-insensitive per the live-test charter."""
    sdk = MagicMock()
    sdk.subjects.list.return_value = [
        MagicMock(subject_key="S1", subject_status="ACTIVE"),
        MagicMock(subject_key="S2", subject_status="Active"),
    ]

    assert discover_subject_key(sdk, "S") == "S1"


def test_discover_site_name_raises_when_none_active() -> None:
    """Sites with no active status should raise even when the list is non-empty."""
    sdk = MagicMock()
    sdk.sites.list.return_value = [
        MagicMock(site_enrollment_status="Closed"),
        MagicMock(site_enrollment_status="Pending"),
    ]

    with pytest.raises(NoLiveDataError, match="No active sites"):
        discover_site_name(sdk, "S")


def test_discover_subject_key_raises_when_none_active() -> None:
    """Subjects with no active status should raise even when the list is non-empty."""
    sdk = MagicMock()
    sdk.subjects.list.return_value = [
        MagicMock(subject_status="Withdrawn"),
        MagicMock(subject_status="Screening"),
    ]

    with pytest.raises(NoLiveDataError, match="No active subjects"):
        discover_subject_key(sdk, "S")
