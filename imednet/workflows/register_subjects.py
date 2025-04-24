"""
Workflow for registering subjects (patients) in iMednet via the Records API.
This workflow is self-contained and does not borrow from record_update.py.
It provides a simple, robust interface for registering one or more subjects.
"""

from typing import Any, List, Optional

from imednet.models.records import RegisterSubjectRequest
from imednet.sdk import ImednetSDK


class RegisterSubjectsWorkflow:
    """
    Workflow for registering one or more subjects (patients) in iMednet.

    Example usage:
        workflow = RegisterSubjectsWorkflow(sdk)
        response = workflow.register_subjects(
            study_key="PHARMADEMO",
            subjects=[
                {
                    "formKey": "REG",
                    "siteName": "Minneapolis",
                    "data": {"textField": "Text value"}
                },
                # ... more subjects ...
            ],
            email_notify="user@domain.com"
        )
    """

    def __init__(self, sdk: "ImednetSDK"):
        self._sdk = sdk

    def register_subjects(
        self,
        study_key: str,
        subjects: List[dict],
        email_notify: Optional[str] = None,
    ) -> Any:
        """
        Register one or more subjects in a study, validating each with RegisterSubjectRequest.
        """
        if not isinstance(subjects, list) or not subjects:
            raise ValueError("'subjects' must be a non-empty list of subject dicts.")
        validated_payload = []
        for idx, subj in enumerate(subjects):
            try:
                model = RegisterSubjectRequest(**subj)
                validated_payload.append(model.model_dump(by_alias=True, exclude_unset=True))
            except Exception as e:
                raise ValueError(f"Subject at index {idx} failed validation: {e}")
        return self._sdk.records.create(
            study_key=study_key,
            records_data=validated_payload,
            email_notify=email_notify,
        )
