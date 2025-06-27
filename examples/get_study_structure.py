import csv
import json
import os

from imednet import ImednetSDK
from imednet.workflows.study_structure import get_study_structure

"""
This script demonstrates how to retrieve the structure of a specific study
using the imednet package.
It initializes the ImednetSDK with API and security keys, then calls the
`get_study_structure` workflow function to fetch the study's structure,
including intervals, forms, and variables.
The script requires the following configuration:
- `api_key`: Your iMednet API key.
- `security_key`: Your iMednet security key.
- `study_key`: The key identifying the target study.
- `base_url`: (Optional) The base URL for the iMednet API if not using the default.
Upon successful retrieval, the script saves the study structure data into an
'study_structure_output' subdirectory relative to the script's location:
1.  `study_structure.json`: Contains the full study structure in JSON format,
    preserving the original hierarchy. Datetime objects are converted to strings.
2.  `study_structure.csv`: Contains a flattened representation of the structure,
    with each row representing a variable within a form within an interval.
    The columns are: intervalId, intervalName, formId, formName, variableName,
    variableLabel. If a form has no variables, a row is still created for the
    form with empty variable details.
If an error occurs during the API call or processing, an error message is printed
to the console.
"""


api_key = "XXXXXXXXXX"
security_key = "XXXXXXXXXX"
base_url = None  # Or set to your custom base URL if needed
study_key = "XXXXXXXXXX"

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)

try:
    structure = get_study_structure(sdk, study_key)
    print(structure)

    # --- Save output ---
    output_dir = os.path.join(os.path.dirname(__file__), "study_structure_output")
    os.makedirs(output_dir, exist_ok=True)

    # Save as JSON (handle datetime serialization)
    json_path = os.path.join(output_dir, "study_structure.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structure.model_dump(by_alias=True), f, indent=2, ensure_ascii=False, default=str)

    # Save as CSV (flattened: interval, form, variable rows)
    csv_path = os.path.join(output_dir, "study_structure.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ["intervalId", "intervalName", "formId", "formName", "variableName", "variableLabel"]
        )
        for interval in structure.intervals:
            for form in interval.forms:
                if form.variables:
                    for var in form.variables:
                        writer.writerow(
                            [
                                interval.interval_id,
                                interval.interval_name,
                                form.form_id,
                                form.form_name,
                                var.variable_name,
                                getattr(var, "variable_label", ""),
                            ]
                        )
                else:
                    writer.writerow(
                        [
                            interval.interval_id,
                            interval.interval_name,
                            form.form_id,
                            form.form_name,
                            "",
                            "",
                        ]
                    )
    print(f"Saved study structure to: {json_path} and {csv_path}")
except Exception as e:
    print(f"Error retrieving study structure: {e}")
