"""Example showing how to list open queries for a study."""

from imednet.sdk import ImednetSDK
from imednet.workflows.query_management import QueryManagementWorkflow

api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"
study_key = "XXXXXXXXXX"
base_url = None  # Optional custom URL

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
workflow = QueryManagementWorkflow(sdk)

try:
    open_queries = workflow.get_open_queries(study_key)
    print(f"Open queries: {len(open_queries)}")
    for q in open_queries[:5]:
        print(f"- Query ID: {q.query_id} Record ID: {q.record_id}")
except Exception as e:
    print(f"Error retrieving queries: {e}")
