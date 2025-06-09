"""Workflow for validating authentication credentials."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for import cycle only
    from ..sdk import ImednetSDK


class CredentialValidationWorkflow:
    """Check API and study keys using the ``studies`` endpoint."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    def validate(self, study_key: str) -> bool:
        """Return ``True`` if ``study_key`` exists in ``studies.list``."""
        studies = self._sdk.studies.list()
        return any(s.study_key == study_key for s in studies)

    def validate_environment(self) -> bool:
        """Validate credentials using ``IMEDNET_STUDY_KEY`` from the environment."""
        study_key = os.getenv("IMEDNET_STUDY_KEY")
        if not study_key:
            raise ValueError("IMEDNET_STUDY_KEY environment variable is not set.")
        return self.validate(study_key)
