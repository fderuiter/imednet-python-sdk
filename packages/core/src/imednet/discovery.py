"""Runtime discovery utilities for live tests and scripts."""

import logging
from collections import Counter

from imednet.sdk import ImednetSDK

logger = logging.getLogger(__name__)

# Site enrollment statuses treated as eligible for smoke/live use.
# ``ENROLLMENT_OPEN`` is the primary write-path status in the observed DEV
# environment.  ``active`` is kept for backward compatibility with environments
# that use a simpler vocabulary.
ELIGIBLE_SITE_STATUSES: frozenset[str] = frozenset({"active", "enrollment_open"})

# Subject workflow statuses treated as eligible for smoke/live use.
# ``Registered``, ``Baseline``, and ``Enrolled`` are the observed DEV values;
# ``active`` is kept for backward compatibility.
ELIGIBLE_SUBJECT_STATUSES: frozenset[str] = frozenset(
    {"active", "registered", "baseline", "enrolled"}
)


def is_site_eligible(site_enrollment_status: str) -> bool:
    """Return ``True`` when *site_enrollment_status* is usable for live tests."""
    return site_enrollment_status.lower() in ELIGIBLE_SITE_STATUSES


def is_subject_eligible(subject_status: str) -> bool:
    """Return ``True`` when *subject_status* is usable for live tests."""
    return subject_status.lower() in ELIGIBLE_SUBJECT_STATUSES


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
    """Return the first eligible site name for ``study_key``.

    A site is eligible when its ``site_enrollment_status`` is one of
    :data:`ELIGIBLE_SITE_STATUSES`.  When no eligible site is found the
    encountered statuses are logged so callers can distinguish *missing data*
    from *unsupported status vocabulary*.
    """
    sites = sdk.sites.list(study_key=study_key)
    encountered: list[str] = []
    for site in sites:
        status = getattr(site, "site_enrollment_status", "")
        if is_site_eligible(status):
            return site.site_name
        encountered.append(status)
    counts = dict(Counter(encountered))
    logger.warning(
        "No eligible sites found for study %s; encountered statuses: %s",
        study_key,
        counts,
    )
    raise NoLiveDataError(f"No active sites available for live tests (encountered: {counts})")


def discover_subject_key(sdk: ImednetSDK, study_key: str) -> str:
    """Return the first eligible subject key for ``study_key``.

    A subject is eligible when its ``subject_status`` is one of
    :data:`ELIGIBLE_SUBJECT_STATUSES`.  When no eligible subject is found the
    encountered statuses are logged so callers can distinguish *missing data*
    from *unsupported status vocabulary*.
    """
    subjects = sdk.subjects.list(study_key=study_key)
    encountered: list[str] = []
    for subject in subjects:
        status = getattr(subject, "subject_status", "")
        if is_subject_eligible(status):
            return subject.subject_key
        encountered.append(status)
    counts = dict(Counter(encountered))
    logger.warning(
        "No eligible subjects found for study %s; encountered statuses: %s",
        study_key,
        counts,
    )
    raise NoLiveDataError(f"No active subjects available for live tests (encountered: {counts})")


def discover_interval_name(sdk: ImednetSDK, study_key: str) -> str:
    """Return the first non-disabled interval name for ``study_key``."""
    intervals = sdk.intervals.list(study_key=study_key)
    for interval in intervals:
        if not getattr(interval, "disabled", False):
            return interval.interval_name
    raise NoLiveDataError(f"No active intervals available for study {study_key}")
