import os

from imednet.sdk import ImednetSDK as ImednetClient

api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL")

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    studies = client.studies.list()
    print(f"Studies found: {len(studies)}")
    if not studies:
        print("No studies returned from API.")
    for study in studies[:1]:
        print(f"- Name: {study.study_name}, Key: {study.study_key}")
        variables = client.variables.list(study_key=study.study_key)
        print(f"Variables for study '{study.study_key}': {len(variables)}")
        if not variables:
            print("No variables returned for this study.")
        for variable in variables[:5]:
            print(f"- Variable Name: {variable.variable_name}, ID: {variable.variable_id}")
except Exception as e:
    print(f"Error: {e}")

# working
