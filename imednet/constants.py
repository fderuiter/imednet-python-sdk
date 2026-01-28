"""
Common constants used throughout the iMednet SDK.

This module centralizes configuration constants to avoid magic numbers
and improve maintainability.
"""

from __future__ import annotations

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "DEFAULT_RETRIES",
    "DEFAULT_BACKOFF_FACTOR",
    "DEFAULT_PAGE_SIZE",
    "LARGE_PAGE_SIZE",
    "MAX_SQLITE_COLUMNS",
    "TERMINAL_JOB_STATES",
]

# API Configuration
DEFAULT_BASE_URL = "https://edc.prod.imednetapi.com"
"""Default base URL for the iMednet API."""

# HTTP Client Configuration
DEFAULT_TIMEOUT = 30.0
"""Default timeout in seconds for HTTP requests."""

DEFAULT_RETRIES = 3
"""Default number of retry attempts for failed requests."""

DEFAULT_BACKOFF_FACTOR = 1.0
"""Default backoff factor for exponential retry delays."""

# Pagination Configuration
DEFAULT_PAGE_SIZE = 100
"""Default number of items to fetch per page."""

LARGE_PAGE_SIZE = 500
"""Page size for endpoints with large metadata (forms, intervals, variables)."""

# Database Limits
MAX_SQLITE_COLUMNS = 2000
"""Maximum number of columns allowed in a SQLite table.

When exporting data to SQLite, tables exceeding this limit must be split
into multiple tables.
"""

# Job States
TERMINAL_JOB_STATES = frozenset({"COMPLETED", "FAILED", "CANCELLED"})
"""Job states that indicate the job has finished processing.

These states are used by the job poller to determine when to stop polling.
Jobs in these states will not transition to another state.
"""
