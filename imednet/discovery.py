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
