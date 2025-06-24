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
1. Replace the placeholder values for `api_key`, `security_key`, and optionally
    `base_url` with your actual credentials and environment URL.
2. Run the script.
"""

api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"
base_url = None  # Or set to your custom base URL if needed
study_key = "XXXXXXXXXX"

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    studies = client.studies.list()
    print("Studies found:")
    for study in studies[:5]:
        print(f"- Name: {study.study_name}, Key: {study.study_key}")
except Exception as e:
    print(f"Error: {e}")
