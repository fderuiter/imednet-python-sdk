import csv
import json
import os

from imednet import ImednetSDK as ImednetClient

"""
A script to retrieve and save study variables from the iMednet API.
This script connects to the iMednet API, retrieves a list of studies and their variables,
and saves the variable information in both JSON and CSV formats.
The script performs the following operations:
1. Connects to iMednet API using provided credentials
2. Retrieves list of available studies
3. For the first study found:
    - Gets all variables for that study
    - Saves variables data to JSON file with full details
    - Saves variables data to CSV file with flattened structure
    - Prints first 5 variables basic information
Required Environment Variables or Constants:
     api_key (str): iMednet API key
     security_key (str): iMednet security key
     base_url (str, optional): Custom base URL for the API
     study_key (str): Study identifier key
Output Files:
     - {output_dir}/variables_{study_key}.json: JSON file containing full variable details
     - {output_dir}/variables_{study_key}.csv: CSV file containing flattened variable information
CSV Fields:
     - variableId: Unique identifier for the variable
     - variableName: Name of the variable
     - formId: ID of the form containing the variable
     - formKey: Key of the form containing the variable
     - formName: Name of the form containing the variable
     - label: Display label for the variable
     - variableType: Type of the variable
     - sequence: Sequence number of the variable
     - revision: Revision number
     - disabled: Disabled status
     - deleted: Deletion status
     - dateCreated: Creation timestamp
     - dateModified: Last modification timestamp
Raises:
     Exception: Any error that occurs during API communication or file operations
"""

api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"
base_url = None  # Or set to your custom base URL if needed
study_key = "XXXXXXXXXX"

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
        else:
            # Save all variables to JSON (with datetime serialization)
            output_dir = os.path.join(os.path.dirname(__file__), "variables_output")
            os.makedirs(output_dir, exist_ok=True)
            json_path = os.path.join(output_dir, f"variables_{study.study_key}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(
                    [v.model_dump(by_alias=True) for v in variables],
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )
            # Save as CSV (flattened)
            csv_path = os.path.join(output_dir, f"variables_{study.study_key}.csv")
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [
                        "variableId",
                        "variableName",
                        "formId",
                        "formKey",
                        "formName",
                        "label",
                        "variableType",
                        "sequence",
                        "revision",
                        "disabled",
                        "deleted",
                        "dateCreated",
                        "dateModified",
                    ]
                )
                for v in variables:
                    writer.writerow(
                        [
                            v.variable_id,
                            v.variable_name,
                            v.form_id,
                            v.form_key,
                            v.form_name,
                            v.label,
                            v.variable_type,
                            v.sequence,
                            v.revision,
                            v.disabled,
                            v.deleted,
                            v.date_created,
                            v.date_modified,
                        ]
                    )
            print(f"Saved variables to: {json_path} and {csv_path}")
        for variable in variables[:5]:
            print(f"- Variable Name: {variable.variable_name}, ID: {variable.variable_id}")
except Exception as e:
    print(f"Error: {e}")
