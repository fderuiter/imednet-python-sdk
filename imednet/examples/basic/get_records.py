import os

from imednet.sdk import ImednetSDK as ImednetClient

"""
Example script demonstrating basic usage of the imednet-python-sdk.
This script initializes the ImednetClient with API credentials,
retrieves a list of studies associated with the account, selects the
first study, and then fetches and prints the first few records
associated with that study.
It showcases:
- Initializing the ImednetSDK client.
- Listing studies using `client.studies.list()`.
- Listing records for a specific study using `client.records.list()`.
- Basic iteration and printing of retrieved data.
- Simple error handling for API calls.
Note:
Ensure the `IMEDNET_API_KEY` and `IMEDNET_SECURITY_KEY` environment variables
are set with your credentials. Optionally set `IMEDNET_BASE_URL` and
`IMEDNET_STUDY_KEY` for custom configurations.
"""

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")  # Optional
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")

if not api_key or not security_key:
    raise RuntimeError(
        "IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables must be set."
    )

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    studies = client.studies.list()
    if not studies:
        print("No studies returned from API.")
    for study in studies[:1]:
        study_key = study.study_key
        records = client.records.list(study_key=study_key)
        print(f"Records for study '{study_key}': {len(records)}")
        for record in records[:5]:
            print(f"- Record ID: {record.record_id}, Subject Key: {record.subject_key}")
except Exception as e:
    print(f"Error: {e}")
