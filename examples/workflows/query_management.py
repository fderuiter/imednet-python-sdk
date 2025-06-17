import os

from imednet.sdk import ImednetSDK

"""Example showing how to work with queries using :class:`QueryManagementWorkflow`.

This script demonstrates:
- Initializing the ImednetSDK
- Retrieving open queries with ``get_open_queries``
- Counting query states with ``get_query_state_counts``

Credentials default to the ``IMEDNET_*`` environment variables if set. Replace
any remaining placeholders before running.
"""

api_key = os.getenv("IMEDNET_API_KEY", "XXXXXXXXXX")
security_key = os.getenv("IMEDNET_SECURITY_KEY", "XXXXXXXXXX")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "XXXXXXXXXX")

try:
    sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
    workflow = sdk.workflows.query_management

    open_queries = workflow.get_open_queries(study_key)
    print(f"Open queries in {study_key}: {len(open_queries)}")

    state_counts = workflow.get_query_state_counts(study_key)
    print(f"Query counts: {state_counts}")
except Exception as e:
    print(f"Error retrieving queries: {e}")
