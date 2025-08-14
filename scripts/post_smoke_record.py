# isort: skip_file
# ruff: noqa: E402, I001
# mypy: ignore-errors
"""Create minimal records via the live API for smoke testing.

Posts one record for each supported scenario:

* subject registration
* new record for an existing subject
* scheduled visit update

Usage:
    poetry run python scripts/post_smoke_record.py [--timeout SECONDS]

``--timeout`` controls how long to wait for the record creation job to
finish before giving up. The default is 90 seconds.
"""

import argparse
import os
import sys
from typing import Any, Dict, Tuple

from imednet.discovery import (
    NoLiveDataError,
    discover_form_key,
    discover_interval_name,
    discover_site_name,
    discover_study_key,
    discover_subject_key,
)
from imednet.models.variables import Variable
from imednet.sdk import ImednetSDK
from imednet.testing.typed_values import canonical_type, value_for


POLL_TIMEOUT = 90


def authenticate() -> ImednetSDK:
    """Build an ``ImednetSDK`` using environment credentials."""
    api_key = os.environ["IMEDNET_API_KEY"]
    security_key = os.environ["IMEDNET_SECURITY_KEY"]
    base_url = os.getenv("IMEDNET_BASE_URL")
    return ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)


def discover_keys(sdk: ImednetSDK) -> Tuple[str, str]:
    """Return the first available study and form keys."""
    study_key = discover_study_key(sdk)
    form_key = discover_form_key(sdk, study_key)
    return study_key, form_key


def discover_identifiers(sdk: ImednetSDK, study_key: str) -> Tuple[str, str, str]:
    """Return the first site, subject, and interval identifiers."""
    site_name = discover_site_name(sdk, study_key)
    subject_key = discover_subject_key(sdk, study_key)
    interval_name = discover_interval_name(sdk, study_key)
    return site_name, subject_key, interval_name


def _select_variables(variables: list[Variable]) -> Dict[str, Variable]:
    """Return one variable per supported type."""

    selected: Dict[str, Variable] = {}
    for var in variables:
        var_type = canonical_type(var.variable_type)
        if var_type and var_type not in selected:
            selected[var_type] = var
    return selected


def _build_data(variables: Dict[str, Variable]) -> Dict[str, Any]:
    """Map variables to deterministic example values."""

    return {var.variable_name: value_for(var.variable_type) for var in variables.values()}


def build_record(
    sdk: ImednetSDK,
    study_key: str,
    form_key: str,
    *,
    site_name: str | None = None,
    subject_key: str | None = None,
    interval_name: str | None = None,
) -> Dict[str, Any]:
    """Construct a record payload for ``form_key``.

    Populates one variable per supported type and includes optional identifiers for
    subject registration or scheduled updates.
    """

    variables = sdk.variables.list(study_key=study_key, formKey=form_key)
    data = _build_data(_select_variables(variables))
    record: Dict[str, Any] = {"formKey": form_key, "data": data}
    if site_name is not None:
        record["siteName"] = site_name
    if subject_key is not None:
        record["subjectKey"] = subject_key
    if interval_name is not None:
        record["intervalName"] = interval_name
    return record


def _extract_error(sdk: ImednetSDK, status: Any) -> str:
    """Return job failure details if available."""
    if getattr(status, "result_url", ""):
        try:
            response = sdk._client.get(status.result_url)  # type: ignore[attr-defined]
            try:
                data = response.json()
            except Exception:  # pragma: no cover - best effort
                data = response.text
            return f"{status.state}: {data}".strip()
        except Exception:  # pragma: no cover - network failures
            return f"{status.state} (see {status.result_url})"
    return status.state


def submit_record(sdk: ImednetSDK, study_key: str, record: Dict[str, Any], *, timeout: int) -> str:
    """Create ``record`` and return the resulting batch ID."""
    job = sdk.records.create(study_key, [record])
    status = sdk.poll_job(study_key, job.batch_id, interval=1, timeout=timeout)
    if status.state != "COMPLETED":
        detail = _extract_error(sdk, status)
        raise RuntimeError(f"Record creation failed: {detail}")
    return status.batch_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=int,
        default=POLL_TIMEOUT,
        help="Seconds to wait for job completion",
    )
    args = parser.parse_args(argv)

    try:
        with authenticate() as sdk:
            study_key, form_key = discover_keys(sdk)
            site_name, subject_key, interval_name = discover_identifiers(sdk, study_key)
            scenarios = [
                {"site_name": site_name},
                {"subject_key": subject_key},
                {"subject_key": subject_key, "interval_name": interval_name},
            ]
            for extra in scenarios:
                record = build_record(sdk, study_key, form_key, **extra)
                submit_record(sdk, study_key, record, timeout=args.timeout)
    except NoLiveDataError as exc:
        print(f"::notice:: Smoke record skipped – {exc}")
        return 0
    except Exception as exc:  # pragma: no cover - runtime safeguard
        print(f"Smoke record failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    sys.exit(main())
