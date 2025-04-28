"""
Workflow for registering subjects (patients) in iMednet via the Records API.
This workflow is self-contained and does not borrow from record_update.py.
It provides a simple, robust interface for registering one or more subjects.
"""

from typing import TYPE_CHECKING, Any, List, Optional

from imednet.models.records import RegisterSubjectRequest

# Use TYPE_CHECKING to avoid circular import at runtime
if TYPE_CHECKING:
    from imednet.sdk import ImednetSDK


class RegisterSubjectsWorkflow:
    """
    Manages the registration of subjects using the iMedNet SDK.

    Attributes:
        _sdk (ImednetSDK): An instance of the ImednetSDK.
    """

    def __init__(self, sdk: "ImednetSDK"):  # Use string literal for type hint
        self._sdk = sdk

    def register_subjects(
        self,
        study_key: str,
        subjects: List[RegisterSubjectRequest],
        email_notify: Optional[str] = None,
    ) -> Any:  # Consider defining a more specific return type if possible
        """
        Registers multiple subjects in the specified study.

        Args:
            study_key: The key identifying the study.
            subjects: A list of RegisterSubjectRequest objects, each defining a subject
                      to be registered.
            email_notify: Optional email address to notify upon completion.

        Returns:
            The response from the API call (e.g., a Job object or similar).

        Raises:
            ApiError: If the API call fails.
        """
        # Convert Pydantic models to dictionaries for the API call
        subjects_data = [s.model_dump(by_alias=True) for s in subjects]

        # Call the SDK's records endpoint to create (register) the subjects
        response = self._sdk.records.create(
            study_key=study_key, records_data=subjects_data, email_notify=email_notify
        )
        return response
