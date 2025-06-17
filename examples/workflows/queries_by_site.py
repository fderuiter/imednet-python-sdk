import os

from imednet import ImednetSDK

"""Retrieve queries for a specific site using :class:`QueryManagementWorkflow`.

This example shows how to initialize the SDK, then use the workflow
method ``get_queries_by_site`` to fetch all queries raised for subjects at
a given site. Credentials default to the ``IMEDNET_*`` environment variables if
set. Replace any remaining placeholders before running.
"""

api_key = os.getenv("IMEDNET_API_KEY", "XXXXXXXXXX")
security_key = os.getenv("IMEDNET_SECURITY_KEY", "XXXXXXXXXX")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "XXXXXXXXXX")
site_name = "SITE001"

try:
    sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
    workflow = sdk.workflows.query_management

    queries = workflow.get_queries_by_site(study_key=study_key, site_key=site_name)
    print(f"Queries for site {site_name}: {len(queries)}")
except Exception as exc:
    print(f"Error fetching queries: {exc}")
