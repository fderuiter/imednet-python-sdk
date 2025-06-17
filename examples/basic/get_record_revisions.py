import os

from imednet.sdk import ImednetSDK as ImednetClient

"""
This script demonstrates how to retrieve record revisions for a specific study
using the iMednet Python SDK.
It initializes the iMednet client with API credentials, lists available studies,
selects the first study found, and then retrieves and prints the record revisions
associated with that study. It prints the total count of revisions and details
for the first five revisions found. Basic error handling is included.
Note: Credentials default to the ``IMEDNET_*`` environment variables if set.
Replace any remaining placeholders and optionally set ``base_url`` before
running.
"""

api_key = os.getenv("IMEDNET_API_KEY", "XXXXXXXXXX")
security_key = os.getenv("IMEDNET_SECURITY_KEY", "XXXXXXXXXX")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "XXXXXXXXXX")

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    studies = client.studies.list()
    if not studies:
        print("No studies returned from API.")
    for study in studies[:1]:
        study_key = study.study_key
        record_revisions = client.record_revisions.list(study_key=study_key)
        print(f"Record Revisions for study '{study_key}': {len(record_revisions)}")
        for rev in record_revisions[:5]:
            print(f"- Revision ID: {rev.record_revision_id}, Record ID: {rev.record_id}")
except Exception as e:
    print(f"Error: {e}")
