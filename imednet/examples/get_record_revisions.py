import os

from imednet.sdk import ImednetSDK as ImednetClient

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")

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

# working
