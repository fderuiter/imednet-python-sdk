from imednet import ImednetSDK as ImednetClient

"""
Example script demonstrating basic usage of the imednet package.
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
Replace "XXXXXXXXXX" placeholders with your actual API key,
security key, and optionally a specific study key if you want to
target a particular study directly. The `base_url` can be left as None
to use the default iMednet API endpoint or set to a custom URL if required.
"""

api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"
base_url = None  # Or set to your custom base URL if needed
study_key = "XXXXXXXXXX"

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
