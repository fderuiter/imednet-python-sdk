from imednet import ImednetSDK as ImednetClient

"""
Example script demonstrating how to retrieve visits from the iMednet API.
This script showcases:
1. Connecting to the iMednet API using the SDK client
2. Listing available studies
3. Retrieving visits for the first study
4. Displaying basic visit information
Requirements:
    - imednet
    - Valid iMednet API credentials (api_key and security_key)
Returns:
    Prints the number of visits for the first study and displays details of up to 5 visits
    including their visit IDs and subject keys.
Raises:
    Exception: Any error that occurs during API communication
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
        visits = client.visits.list(study_key=study_key)
        print(f"Visits for study '{study_key}': {len(visits)}")
        for visit in visits[:5]:
            print(f"- Visit ID: {visit.visit_id}, Subject Key: {visit.subject_key}")
except Exception as e:
    print(f"Error: {e}")
