from typing import Any, Dict

from imednet import ImednetSDK
from imednet.workflows.data_extraction import DataExtractionWorkflow

"""Example using :class:`DataExtractionWorkflow.extract_audit_trail`.

This script retrieves audit trail entries for a study. It demonstrates
initializing the SDK and calling ``extract_audit_trail`` with optional
filters. Replace the placeholder credentials and study key before running.
"""

api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"
base_url = None  # Or set to your custom base URL if needed
study_key = "XXXXXXXXXX"

try:
    sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
    workflow = DataExtractionWorkflow(sdk)

    filter_dict: Dict[str, Any] = {"user": "some.user@example.com"}

    revisions = workflow.extract_audit_trail(
        study_key=study_key,
        start_date="2024-01-01",
        end_date="2024-12-31",
        user_filter=filter_dict,
    )
    print(f"Audit trail entries returned: {len(revisions)}")
except Exception as exc:
    print(f"Error retrieving audit trail: {exc}")
