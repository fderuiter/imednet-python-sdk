"""Runtime discovery utilities for live tests and scripts."""

from imednet.sdk import ImednetSDK


class NoLiveDataError(RuntimeError):
    """Raised when required live data cannot be found."""


def discover_study_key(sdk: ImednetSDK) -> str:
    """Return the first study key available for the provided SDK."""
    studies = sdk.studies.list()
    if not studies:
        raise NoLiveDataError("No studies available for live tests")
    return studies[0].study_key


def discover_form_key(sdk: ImednetSDK, study_key: str) -> str:
    """Return the first subject record form key for ``study_key``."""
    forms = sdk.forms.list(study_key=study_key)
    for form in forms:
        if form.subject_record_report and not form.disabled:
            return form.form_key
    raise NoLiveDataError("No forms available for record creation")


def discover_site_name(sdk: ImednetSDK, study_key: str) -> str:
    """Return the first active site name for ``study_key``."""
    sites = sdk.sites.list(study_key=study_key)
    for site in sites:
        if getattr(site, "site_enrollment_status", "").lower() == "active":
            return site.site_name
    raise NoLiveDataError("No active sites available for live tests")


def discover_subject_key(sdk: ImednetSDK, study_key: str) -> str:
    """Return the first active subject key for ``study_key``."""
    subjects = sdk.subjects.list(study_key=study_key)
    for subject in subjects:
        if getattr(subject, "subject_status", "").lower() == "active":
            return subject.subject_key
    raise NoLiveDataError("No active subjects available for live tests")


def discover_interval_name(sdk: ImednetSDK, study_key: str) -> str:
    """Return the first non-disabled interval name for ``study_key``."""
    intervals = sdk.intervals.list(study_key=study_key)
    for interval in intervals:
        if not getattr(interval, "disabled", False):
            return interval.interval_name
    raise NoLiveDataError("No active intervals available for live tests")
