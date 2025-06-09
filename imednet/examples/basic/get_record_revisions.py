from imednet.sdk import ImednetSDK as ImednetClient
import os

"""
This script demonstrates how to retrieve record revisions for a specific study
using the iMednet Python SDK.
It initializes the iMednet client with API credentials, lists available studies,
selects the first study found, and then retrieves and prints the record revisions
associated with that study. It prints the total count of revisions and details
for the first five revisions found. Basic error handling is included.
Set your API credentials via the environment variables `IMEDNET_API_KEY` and
`IMEDNET_SECURITY_KEY`. Optionally configure `IMEDNET_BASE_URL` and
`IMEDNET_STUDY_KEY`.
"""

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")  # Optional
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")

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
