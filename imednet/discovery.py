"""Runtime discovery utilities for live tests and scripts."""

from imednet.sdk import ImednetSDK


class NoLiveDataError(RuntimeError):
    """Raised when required live data cannot be found for tests or scripts."""


def discover_study_key(sdk: ImednetSDK) -> str:
    """Discover and return the first available study key.

    Args:
        sdk: An initialized ImednetSDK instance.

    Returns:
        The first study key found.

    Raises:
        NoLiveDataError: If no studies are available.
    """
    studies = sdk.studies.list()
    if not studies:
        raise NoLiveDataError("No studies available for live tests")
    return studies[0].study_key


def discover_form_key(sdk: ImednetSDK, study_key: str) -> str:
    """Discover and return the first available subject record form key.

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study to search in.

    Returns:
        The first form key found that is a subject record report and not disabled.

    Raises:
        NoLiveDataError: If no suitable forms are available.
    """
    forms = sdk.forms.list(study_key=study_key)
    for form in forms:
        if form.subject_record_report and not form.disabled:
            return form.form_key
    raise NoLiveDataError("No forms available for record creation")


def discover_site_name(sdk: ImednetSDK, study_key: str) -> str:
    """Discover and return the first active site name.

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study to search in.

    Returns:
        The name of the first active site found.

    Raises:
        NoLiveDataError: If no active sites are available.
    """
    sites = sdk.sites.list(study_key=study_key)
    for site in sites:
        if getattr(site, "site_enrollment_status", "").lower() == "active":
            return site.site_name
    raise NoLiveDataError("No active sites available for live tests")


def discover_subject_key(sdk: ImednetSDK, study_key: str) -> str:
    """Discover and return the first active subject key.

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study to search in.

    Returns:
        The key of the first active subject found.

    Raises:
        NoLiveDataError: If no active subjects are available.
    """
    subjects = sdk.subjects.list(study_key=study_key)
    for subject in subjects:
        if getattr(subject, "subject_status", "").lower() == "active":
            return subject.subject_key
    raise NoLiveDataError("No active subjects available for live tests")


def discover_interval_name(sdk: ImednetSDK, study_key: str) -> str:
    """Discover and return the first non-disabled interval name.

    Args:
        sdk: An initialized ImednetSDK instance.
        study_key: The key of the study to search in.

    Returns:
        The name of the first non-disabled interval found.

    Raises:
        NoLiveDataError: If no active intervals are available.
    """
    intervals = sdk.intervals.list(study_key=study_key)
    for interval in intervals:
        if not getattr(interval, "disabled", False):
            return interval.interval_name
    raise NoLiveDataError("No active intervals available for live tests")
