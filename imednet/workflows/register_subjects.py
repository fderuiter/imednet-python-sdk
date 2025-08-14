"""
Workflow for registering subjects (patients) in iMednet via the Records API.
This workflow is self-contained and does not borrow from record_update.py.
It provides a simple, robust interface for registering one or more subjects.
"""

from typing import TYPE_CHECKING, List, Optional

from imednet.core.exceptions import ApiError
from imednet.models.jobs import Job
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
    ) -> Job:
        """
        Registers multiple subjects in the specified study.
        Sites and subject identifiers are validated before submission.

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
        # Validate sites and subjects before posting
        sites = {s.site_name for s in self._sdk.sites.list(study_key=study_key)}
        errors: list[str] = []
        for idx, subj in enumerate(subjects):
            if not subj.site_name:
                errors.append(f"Index {idx}: siteName is required")
            elif subj.site_name not in sites:
                errors.append(f"Index {idx}: site '{subj.site_name}' not found")
            if not subj.subject_key:
                errors.append(f"Index {idx}: subjectKey is required")
            else:
                try:
                    self._sdk.subjects.get(study_key, subj.subject_key)
                except (ApiError, ValueError):
                    errors.append(
                        f"Index {idx}: subject with subjectKey {subj.subject_key} not found"
                    )

        if errors:
            raise ValueError("; ".join(errors))

        subjects_data = [s.model_dump(by_alias=True) for s in subjects]

        response = self._sdk.records.create(
            study_key=study_key, records_data=subjects_data, email_notify=email_notify
        )
        return response
