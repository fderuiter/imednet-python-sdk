"""SPI for utility functions."""

from imednet.utils.dates import format_iso_datetime, parse_iso_datetime
from imednet.utils.db import get_sqlite_connection, sqlite_connection
from imednet.utils.filters import build_filter_string
from imednet.utils.job_poller import (
    AsyncJobPoller,
    JobFailedError,
    JobPoller,
    JobPollSummary,
    JobProgressCallback,
    JobStatusEvent,
    JobTimeoutError,
    evaluate_job_state,
)
from imednet.utils.security import mask_clinical_phi, sanitize_csv_formula
from imednet.utils.serialization import flatten
from imednet.utils.url import redact_sensitive_text
from imednet.utils.validators import is_boolean_token, is_missing_value, parse_bool

__all__ = [
    "AsyncJobPoller",
    "JobFailedError",
    "JobPollSummary",
    "JobPoller",
    "JobProgressCallback",
    "JobStatusEvent",
    "JobTimeoutError",
    "build_filter_string",
    "evaluate_job_state",
    "flatten",
    "format_iso_datetime",
    "is_boolean_token",
    "is_missing_value",
    "mask_clinical_phi",
    "parse_bool",
    "parse_iso_datetime",
    "redact_sensitive_text",
    "sanitize_csv_formula",
    "get_sqlite_connection",
    "sqlite_connection",
]
