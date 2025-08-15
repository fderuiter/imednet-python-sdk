from unittest.mock import Mock

import pytest

from imednet.discovery import (
    NoLiveDataError,
    discover_form_key,
    discover_interval_name,
    discover_site_name,
    discover_subject_key,
)
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.sites import Site
from imednet.models.subjects import Subject


def test_discover_form_key_chooses_subject_form() -> None:
    sdk = Mock()
    sdk.forms.list.return_value = [
        Form(study_key="S", form_key="SS", subject_record_report=False),
        Form(study_key="S", form_key="F1", subject_record_report=True, disabled=True),
        Form(study_key="S", form_key="F2", subject_record_report=True, disabled=False),
    ]

    assert discover_form_key(sdk, "S") == "F2"


def test_discover_form_key_raises_when_no_valid_forms() -> None:
    sdk = Mock()
    sdk.forms.list.return_value = [Form(study_key="S", form_key="SS", subject_record_report=False)]

    with pytest.raises(NoLiveDataError):
        discover_form_key(sdk, "S")


def test_discover_site_name_returns_active_site() -> None:
    sdk = Mock()
    sdk.sites.list.return_value = [
        Site(study_key="S", site_name="Closed", site_enrollment_status="Closed"),
        Site(study_key="S", site_name="Open", site_enrollment_status="Active"),
    ]

    assert discover_site_name(sdk, "S") == "Open"
    sdk.sites.list.assert_called_once_with(study_key="S")


def test_discover_site_name_raises_when_no_active() -> None:
    sdk = Mock()
    sdk.sites.list.return_value = [
        Site(study_key="S", site_name="X", site_enrollment_status="Closed")
    ]

    with pytest.raises(NoLiveDataError):
        discover_site_name(sdk, "S")


def test_discover_subject_key_returns_active_subject() -> None:
    sdk = Mock()
    sdk.subjects.list.return_value = [
        Subject(study_key="S", subject_key="S1", subject_status="Closed"),
        Subject(study_key="S", subject_key="S2", subject_status="Active"),
    ]

    assert discover_subject_key(sdk, "S") == "S2"
    sdk.subjects.list.assert_called_once_with(study_key="S")


def test_discover_subject_key_raises_when_no_active() -> None:
    sdk = Mock()
    sdk.subjects.list.return_value = [
        Subject(study_key="S", subject_key="S1", subject_status="Closed")
    ]

    with pytest.raises(NoLiveDataError):
        discover_subject_key(sdk, "S")


def test_discover_interval_name_returns_active_interval() -> None:
    sdk = Mock()
    sdk.intervals.list.return_value = [
        Interval(study_key="S", interval_name="I1", disabled=True),
        Interval(study_key="S", interval_name="I2", disabled=False),
    ]

    assert discover_interval_name(sdk, "S") == "I2"
    sdk.intervals.list.assert_called_once_with(study_key="S")


def test_discover_interval_name_raises_when_all_disabled() -> None:
    sdk = Mock()
    sdk.intervals.list.return_value = [Interval(study_key="S", interval_name="I1", disabled=True)]

    with pytest.raises(NoLiveDataError):
        discover_interval_name(sdk, "S")
