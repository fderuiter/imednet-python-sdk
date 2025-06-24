from imednet import ImednetSDK as ImednetClient

"""
This script demonstrates how to retrieve coding information from the iMednet API
using the imednet package.
It initializes the ImednetClient with API credentials, lists the available studies,
retrieves the codings for the first study found, and prints the total count
of codings along with details for the first five codings.
Requires:
- imednet installed (`pip install imednet`)
- Valid API key and security key (replace placeholders).
Usage:
1. Replace the placeholder values for `api_key` and `security_key`.
2. Optionally set `base_url` if using a custom iMednet instance.
3. Run the script.
The script will output:
- The total number of codings found for the first study accessed via the API key.
- The Coding ID and Variable name for the first 5 codings (if available).
- An error message if any issues occur during the API interaction.
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
        codings = client.codings.list(study_key=study_key)
        print(f"Codings for study '{study_key}': {len(codings)}")
        for coding in codings[:5]:
            print(f"- Coding ID: {coding.coding_id}, Variable: {coding.variable}")
except Exception as e:
    print(f"Error: {e}")
