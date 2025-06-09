import os

from imednet.sdk import ImednetSDK as ImednetClient

"""
Example script demonstrating how to retrieve users from an iMedNet study using the iMedNet SDK.
This script shows how to:
1. Initialize the iMedNet SDK client with authentication credentials
2. List available studies
3. Get users for the first study
4. Print basic user information for up to 5 users
Required Parameters:
    api_key (str): API key for authentication
    security_key (str): Security key for authentication
    base_url (str, optional): Custom base URL if needed, defaults to None
    study_key (str): Study identifier key
Returns:
    Prints user information to console including:
    - Number of users in the study
    - Login and name details for up to 5 users
Raises:
    Exception: Any errors during API communication or data retrieval
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
        users = client.users.list(study_key=study_key)
        print(f"Users for study '{study_key}': {len(users)}")
        for user in users[:5]:
            print(f"- User Login: {user.login}, Name: {user.name}")
except Exception as e:
    print(f"Error: {e}")
