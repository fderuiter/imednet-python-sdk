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
        visits = client.visits.list(study_key=study_key)
        print(f"Visits for study '{study_key}': {len(visits)}")
        for visit in visits[:5]:
            print(f"- Visit ID: {visit.visit_id}, Subject Key: {visit.subject_key}")
except Exception as e:
    print(f"Error: {e}")

# working
