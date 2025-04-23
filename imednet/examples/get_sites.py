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
        sites = client.sites.list(study_key=study_key)
        print(f"Sites for study '{study_key}': {len(sites)}")
        for site in sites[:5]:
            print(f"- Site Name: {site.site_name}, ID: {site.site_id}")
except Exception as e:
    print(f"Error: {e}")

# working
