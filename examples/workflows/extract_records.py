import os
from typing import Any, Dict

from imednet.sdk import ImednetSDK
from imednet.workflows.data_extraction import DataExtractionWorkflow

"""Example using :class:`DataExtractionWorkflow.extract_records_by_criteria`.

This script initializes the SDK and workflow, then retrieves records for a study
filtered by subject and visit attributes. Credentials default to the
``IMEDNET_*`` environment variables if set. Replace any remaining placeholders
before running.
"""

api_key = os.getenv("IMEDNET_API_KEY", "XXXXXXXXXX")
security_key = os.getenv("IMEDNET_SECURITY_KEY", "XXXXXXXXXX")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "XXXXXXXXXX")

try:
    sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
    workflow = DataExtractionWorkflow(sdk)

    subject_filter: Dict[str, Any] = {"subjectStatus": "Active"}
    visit_filter: Dict[str, Any] = {"intervalName": "Baseline"}

    records = workflow.extract_records_by_criteria(
        study_key=study_key,
        subject_filter=subject_filter,
        visit_filter=visit_filter,
    )
    print(f"Number of records matching criteria: {len(records)}")
except Exception as e:
    print(f"Error extracting records: {e}")
