"""Placeholder for mutable SDK context."""

# Purpose:
# This module provides a way to manage mutable state or configuration that might
# affect multiple API calls, such as a default `study_key`.

# Implementation:
# 1. Define a class `Context` (potentially using `dataclasses` or `pydantic`).
# 2. Include attributes for configurable defaults, e.g., `default_study_key: Optional[str] = None`.
# 3. The `Client` or `MednetSdk` might hold an instance of this `Context`.
# 4. Endpoint methods could check this context for default values if specific arguments
#    (like `study_key`) are not provided by the user.
# 5. Provide methods on `MednetSdk` to get/set values in the context
#       (e.g., `sdk.set_default_study("STUDY123")`).

# Integration:
# - An instance can be created and managed by the `MednetSdk`.
# - Potentially passed to or accessed by `Endpoint` classes to resolve default parameters.
# - Allows users to set common parameters once instead of repeating them in every call.


class Context:
    """Manages mutable SDK context, like default study key."""

    pass
