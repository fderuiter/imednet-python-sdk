import os

from imednet.sdk import ImednetSDK as ImednetClient

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    studies = client.studies.list()
    print("Studies found:")
    for study in studies[:5]:
        print(f"- Name: {study.study_name}, Key: {study.study_key}")
except Exception as e:
    print(f"Error: {e}")

# working
