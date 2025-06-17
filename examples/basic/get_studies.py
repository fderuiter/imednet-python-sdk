import os

from imednet import ImednetSDK as ImednetClient

"""
Example script demonstrating how to list available studies using the iMednet SDK.
This script initializes the ImednetClient with the necessary API credentials
(API key and security key). It then calls the `studies.list()` method to retrieve
a list of studies accessible with the provided credentials. Finally, it prints
the name and key of the first 5 studies found. If any error occurs during the
process, it prints an error message.
Prerequisites:
- An active iMednet account with API access.
- Your API key and security key.
Usage:
1. Credentials default to the ``IMEDNET_*`` environment variables if set.
   Replace any remaining ``XXXXXXXXXX`` placeholders and, if needed,
   ``base_url`` with your environment URL.
2. Run the script.
"""

api_key = os.getenv("IMEDNET_API_KEY", "XXXXXXXXXX")
security_key = os.getenv("IMEDNET_SECURITY_KEY", "XXXXXXXXXX")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "XXXXXXXXXX")

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    studies = client.studies.list()
    print("Studies found:")
    for study in studies[:5]:
        print(f"- Name: {study.study_name}, Key: {study.study_key}")
except Exception as e:
    print(f"Error: {e}")
