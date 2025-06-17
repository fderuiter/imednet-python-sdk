from imednet import ImednetSDK
from imednet.workflows.subject_data import SubjectDataWorkflow

"""Example retrieving all data for a single subject via ``SubjectDataWorkflow``.

This script demonstrates how to:
1. Initialize the :class:`ImednetSDK` client.
2. Use :class:`SubjectDataWorkflow` to gather subject details, visits, records, and queries.
3. Display a summary of the returned information.

Replace the ``XXXXXXXXXX`` placeholders with real values before running.
"""

api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"
base_url = None  # Or set to your custom base URL if needed
study_key = "XXXXXXXXXX"
subject_key = "XXXXXXXXXX"

try:
    sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)
    workflow = SubjectDataWorkflow(sdk)
    data = workflow.get_all_subject_data(study_key=study_key, subject_key=subject_key)

    print("Subject Details:")
    print(data.subject_details)

    print(f"Visits ({len(data.visits)}):")
    for visit in data.visits[:5]:
        print(f" - Visit ID: {visit.visit_id}, Interval: {visit.interval_name}")

    print(f"Records ({len(data.records)}):")
    for record in data.records[:5]:
        print(f" - Record ID: {record.record_id}, Form ID: {record.form_id}")

    print(f"Queries ({len(data.queries)}):")
    for query in data.queries[:5]:
        print(f" - Annotation ID: {query.annotation_id}, Type: {query.type}")
except Exception as exc:
    print(f"Error fetching subject data: {exc}")
