"""
Workflow for registering subjects (patients) in iMednet via the Records API.
This workflow is self-contained and does not borrow from record_update.py.
It provides a simple, robust interface for registering one or more subjects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from imednet.models.records import RegisterSubjectRequest

# Use TYPE_CHECKING to avoid circular import at runtime
if TYPE_CHECKING:
    from imednet.sdk import AsyncImednetSDK, ImednetSDK


class RegisterSubjectsWorkflow:
    """
    Manages the registration of subjects using the iMedNet SDK.

    Attributes:
        _sdk (ImednetSDK): An instance of the ImednetSDK.
    """

    def __init__(self, sdk: "ImednetSDK | AsyncImednetSDK"):
        from ..sdk import AsyncImednetSDK

        self._sdk = sdk
        self._is_async = isinstance(sdk, AsyncImednetSDK)

    def register_subjects(
        self,
        study_key: str,
        subjects: List[RegisterSubjectRequest],
        email_notify: Optional[str] = None,
    ) -> Any:
        """
        Registers multiple subjects in the specified study.

        Args:
            study_key: The key identifying the study.
            subjects: A list of RegisterSubjectRequest objects, each defining a subject
                      to be registered.
            email_notify: Optional email address to notify upon completion.

        Returns:
            A :class:`Job` object representing the background job
            created for the registration request.

        Raises:
            ApiError: If the API call fails.
        """
        subjects_data = [s.model_dump(by_alias=True) for s in subjects]
        if self._is_async:
            return self._sdk.records.async_create(
                study_key=study_key,
                records_data=subjects_data,
                email_notify=email_notify,
            )
        return self._sdk.records.create(
            study_key=study_key,
            records_data=subjects_data,
            email_notify=email_notify,
        )
