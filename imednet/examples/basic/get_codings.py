from imednet.sdk import ImednetSDK as ImednetClient
import os

"""
This script demonstrates how to retrieve coding information from the iMednet API
using the imednet-python-sdk.
It initializes the ImednetClient with API credentials, lists the available studies,
retrieves the codings for the first study found, and prints the total count
of codings along with details for the first five codings.
Requires:
- imednet-python-sdk installed (`pip install imednet-python-sdk`)
- Valid API key and security key provided via environment variables.
Usage:
1. Ensure `IMEDNET_API_KEY` and `IMEDNET_SECURITY_KEY` environment variables are set.
2. Optionally set `IMEDNET_BASE_URL` and `IMEDNET_STUDY_KEY` if using a custom iMednet instance.
3. Run the script.
The script will output:
- The total number of codings found for the first study accessed via the API key.
- The Coding ID and Variable name for the first 5 codings (if available).
- An error message if any issues occur during the API interaction.
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
        codings = client.codings.list(study_key=study_key)
        print(f"Codings for study '{study_key}': {len(codings)}")
        for coding in codings[:5]:
            print(f"- Coding ID: {coding.coding_id}, Variable: {coding.variable}")
except Exception as e:
    print(f"Error: {e}")
