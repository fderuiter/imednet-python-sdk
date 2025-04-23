"""Placeholder for date and time utility functions."""

import datetime

# Purpose:
# This module provides helper functions for parsing and formatting dates and times,
# particularly handling the ISO 8601 format commonly used in APIs, including timezone awareness.

# Implementation:
# 1. Define functions like:
#    - `parse_iso_datetime(dt_str: str | None) -> datetime.datetime | None`:
#      - Takes an ISO 8601 string (potentially with 'Z' or offset).
#      - Uses `datetime.datetime.fromisoformat` or a robust parsing library.
#      - Handles potential `None` input.
#      - Returns a timezone-aware `datetime` object (preferably UTC).
#    - `format_iso_datetime(dt: datetime.datetime | None) -> str | None`:
#      - Takes a `datetime` object.
#      - Converts to UTC if necessary.
#      - Formats it into the standard ISO 8601 format with 'Z' for UTC.
#      - Handles potential `None` input.
# 2. Ensure proper handling of timezones.

# Integration:
# - Used by `Models` when deserializing date fields from API responses.
# - Used by `Endpoint` or `Workflow` methods when constructing requests
#       that require date parameters.
# - Provides consistent date handling throughout the SDK.


def parse_iso_datetime(dt_str: str | None) -> datetime.datetime | None:
    """Parses an ISO 8601 string into a timezone-aware datetime object (UTC)."""
    if dt_str is None:
        return None
    try:
        # Handle 'Z' for UTC explicitly if needed by older Python versions or specific libraries
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        dt = datetime.datetime.fromisoformat(dt_str)
        # If timezone naive, assume UTC (or raise error depending on desired strictness)
        if dt.tzinfo is None:
            # return dt.replace(tzinfo=datetime.timezone.utc) # Option 1: Assume UTC
            raise ValueError(
                "Naive datetime encountered, expected timezone-aware ISO string"
            )  # Option 2: Be strict
        # Convert to UTC
        return dt.astimezone(datetime.timezone.utc)
    except ValueError as e:
        # Log the error or re-raise a custom exception
        print(f"Error parsing date string '{dt_str}': {e}")
        # Or raise DateParseError(f"Invalid ISO date format: {dt_str}") from e
        return None  # Or re-raise


def format_iso_datetime(dt: datetime.datetime | None) -> str | None:
    """Formats a datetime object into an ISO 8601 string in UTC ('Z' notation)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume UTC or raise error
        dt = dt.replace(tzinfo=datetime.timezone.utc)
        # raise ValueError("Cannot format naive datetime, timezone required")

    # Convert to UTC and format
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
