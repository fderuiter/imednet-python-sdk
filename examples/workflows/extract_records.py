from typing import Any, Dict

from imednet import ImednetSDK
from imednet.workflows.data_extraction import DataExtractionWorkflow

"""Example using :class:`DataExtractionWorkflow.extract_records_by_criteria`.

This script initializes the SDK and workflow, then retrieves records for a study
filtered by subject and visit attributes. Update the credential placeholders
before running.
"""

api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"
base_url = None  # Or set to your custom base URL if needed
study_key = "XXXXXXXXXX"

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
