# isort: skip_file
# ruff: noqa: E402, I001
"""Create a minimal record via the live API for smoke testing."""

import os
import sys
from typing import Any, Dict, Tuple

from imednet.discovery import NoLiveDataError, discover_form_key, discover_study_key
from imednet.sdk import ImednetSDK


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


def build_record(sdk: ImednetSDK, study_key: str, form_key: str) -> Dict[str, Any]:
    """Construct a minimal record payload for ``form_key``."""
    variables = sdk.variables.list(study_key=study_key, formKey=form_key)
    data: Dict[str, Any] = {}
    if variables:
        data[variables[0].variable_name] = ""
    return {"formKey": form_key, "data": data}


def submit_record(sdk: ImednetSDK, study_key: str, record: Dict[str, Any]) -> str:
    """Create ``record`` and return the resulting batch ID."""
    job = sdk.records.create(study_key, [record])
    status = sdk.poll_job(study_key, job.batch_id, interval=1, timeout=POLL_TIMEOUT)
    if status.state != "COMPLETED":
        raise RuntimeError(f"Record creation failed: {status.state}")
    return status.batch_id


def main() -> int:
    try:
        with authenticate() as sdk:
            study_key, form_key = discover_keys(sdk)
            record = build_record(sdk, study_key, form_key)
            submit_record(sdk, study_key, record)
    except NoLiveDataError as exc:
        print(f"::notice:: Smoke record skipped – {exc}")
        return 0
    except Exception as exc:  # pragma: no cover - runtime safeguard
        print(f"Smoke record failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    sys.exit(main())
