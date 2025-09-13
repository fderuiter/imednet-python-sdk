"""
Manage mutable SDK context, like default study key.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Context:
    """Holds default values for SDK calls, such as default study key."""

    #: Default study key for API calls.
    #: :noindex:
    default_study_key: Optional[str] = None

    def set_default_study_key(self, study_key: str) -> None:
        """
        Set the default study key to use for subsequent API calls.

        Args:
            study_key: The study key string.
        """
        self.default_study_key = study_key

    def clear_default_study_key(self) -> None:
        """
        Clear the default study key.
        """
        self.default_study_key = None
