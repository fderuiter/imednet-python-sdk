import os

from imednet.sdk import ImednetSDK as ImednetClient

"""
This script demonstrates how to use the Imednet Python SDK to retrieve a list of studies
and then list the sites associated with the first study found.
It initializes the ImednetClient with API credentials, fetches the list of studies
accessible with those credentials, selects the first study, and then retrieves
and prints the details (name and ID) of the first few sites belonging to that study.
Requires:
- An active Imednet account with API access.
- API Key and Security Key for authentication.
- The `imednet-python-sdk` package installed (`pip install imednet-python-sdk`).
Usage:
1. Ensure the environment variables `IMEDNET_API_KEY` and `IMEDNET_SECURITY_KEY` are set.
   Optionally configure `IMEDNET_BASE_URL` and `IMEDNET_STUDY_KEY`.
2. Run the script. It will print the total number of sites for the first study found
    and the details of up to the first five sites.
3. If an error occurs during the API interaction, an error message will be printed.
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
        sites = client.sites.list(study_key=study_key)
        print(f"Sites for study '{study_key}': {len(sites)}")
        for site in sites[:5]:
            print(f"- Site Name: {site.site_name}, ID: {site.site_id}")
except Exception as e:
    print(f"Error: {e}")
