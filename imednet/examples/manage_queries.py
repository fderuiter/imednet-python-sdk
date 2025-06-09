import os

from imednet.sdk import ImednetSDK
from imednet.workflows.query_management import QueryManagementWorkflow

"""Example for using :class:`QueryManagementWorkflow` to inspect queries.

This script fetches open queries for the configured study and shows how to
retrieve queries for a specific subject and summarize query states.

Environment variables required:
    - ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY`` for authentication.
    - ``IMEDNET_STUDY_KEY`` identifying the study to inspect.
Optional variables:
    - ``IMEDNET_SUBJECT_KEY`` to fetch queries for a specific subject.
    - ``IMEDNET_BASE_URL`` if using a non-default iMednet URL.
"""

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")
subject_key = os.getenv("IMEDNET_SUBJECT_KEY")

if not api_key or not security_key:
    raise RuntimeError(
        "IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables must be set."
    )

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
workflow = QueryManagementWorkflow(sdk)

try:
    open_queries = workflow.get_open_queries(study_key)
    print(f"Found {len(open_queries)} open queries for study '{study_key}'.")

    if subject_key:
        subj_queries = workflow.get_queries_for_subject(study_key, subject_key)
        print(f"Subject {subject_key} has {len(subj_queries)} queries.")

    counts = workflow.get_query_state_counts(study_key)
    print("Query state counts:", counts)
except Exception as e:
    print(f"Error retrieving queries: {e}")
