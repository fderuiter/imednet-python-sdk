from imednet import ImednetSDK as ImednetClient

"""
Example script demonstrating how to retrieve subjects from iMednet studies using the iMednet SDK.
This script:
1. Initializes the iMednet client with API credentials
2. Retrieves a list of available studies
3. For the first study, retrieves and displays information about its subjects
4. Prints the subject key and status for up to 5 subjects
Required environment variables or configurations:
    - api_key (str): Your iMednet API key
    - security_key (str): Your iMednet security key
    - base_url (str, optional): Custom base URL for the API endpoint
    - study_key (str): The study identifier
Returns:
    None. Prints subject information to standard output.
Raises:
    Exception: Any errors that occur during API communication
"""

api_key = "XXX"
security_key = "XXX"
base_url = None  # Or set to your custom base URL if needed
study_key = "XXX"

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    studies = client.studies.list()
    if not studies:
        print("No studies returned from API.")
    for study in studies[:1]:
        study_key = study.study_key
        subjects = client.subjects.list(study_key=study_key)
        print(f"Subjects for study '{study_key}': {len(subjects)}")
        for subject in subjects[:5]:
            print(f"- Subject Key: {subject.subject_key}, Status: {subject.subject_status}")
except Exception as e:
    print(f"Error: {e}")
