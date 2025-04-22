# examples/create_new_record.py
"""
Example script demonstrating how to create a new record (e.g., for a specific form)
for a subject using the iMednet Python SDK.
"""
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import ImednetException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")

# --- Configuration ---
# Specify the Study OID, Subject Key, and Form OID for the new record
TARGET_STUDY_OID = "STUDY_OID_HERE"      # Replace with a valid Study OID
TARGET_SUBJECT_KEY = "SUBJECT_KEY_HERE" # Replace with a valid Subject Key
TARGET_FORM_OID = "FORM_OID_HERE"        # Replace with the OID of the form to create a record for
TARGET_SITE_OID = "SITE_OID_HERE"        # Replace with the OID of the subject's site
TARGET_VISIT_OID = "VISIT_OID_HERE"      # Replace with the OID of the relevant visit/event

# Define the data for the new record. The structure depends heavily on the specific form.
# This is a *highly simplified* example. You MUST adapt this to match the variables
# and data types expected by your specific form (TARGET_FORM_OID).
# Consult the iMednet API documentation or form definition for the correct structure.
NEW_RECORD_DATA = {
    "RecordDate": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), # Example format, adjust if needed
    "RecordActive": True,
    # --- Form-Specific Data Items --- 
    # Replace these with actual variable OIDs and values for your form
    "VAR_OID_1": "Some text value",
    "VAR_OID_2": 123.45,
    "VAR_OID_DATE": "2025-04-21", # Example date format
    # ... add all required and optional data items for the form ...
}
# ---------------------

def main():
    """Main function to create a new record."""
    if not API_KEY or not BASE_URL:
        logging.error("API Key or Base URL not configured. Set IMEDNET_API_KEY and IMEDNET_BASE_URL environment variables.")
        return

    if any(val == "STUDY_OID_HERE" or val == "SUBJECT_KEY_HERE" or val == "FORM_OID_HERE" or val == "SITE_OID_HERE" or val == "VISIT_OID_HERE" for val in [TARGET_STUDY_OID, TARGET_SUBJECT_KEY, TARGET_FORM_OID, TARGET_SITE_OID, TARGET_VISIT_OID]):
        logging.warning("Please replace placeholder OIDs/Keys (STUDY_OID_HERE, SUBJECT_KEY_HERE, etc.) with actual values in the script.")
        return

    if "VAR_OID_1" in NEW_RECORD_DATA: # Check if the example data hasn't been updated
        logging.warning("The NEW_RECORD_DATA dictionary contains example variable OIDs (VAR_OID_1, etc.). You MUST replace these with the actual variable OIDs and corresponding values for your target form.")
        # return # Uncomment this line to prevent running with example data

    try:
        # Initialize the client
        client = ImednetClient(base_url=BASE_URL, api_key=API_KEY)
        logging.info("iMednet client initialized successfully.")

        # --- Create New Record ---
        logging.info(f"Attempting to create a new record for form '{TARGET_FORM_OID}' for subject '{TARGET_SUBJECT_KEY}' in study '{TARGET_STUDY_OID}'...")

        # Assumes client.records.create() exists and takes necessary identifiers and data.
        # The exact parameters (study_oid, subject_key, form_oid, visit_oid, site_oid, data) might differ.
        created_record = client.records.create(
            study_oid=TARGET_STUDY_OID,
            subject_key=TARGET_SUBJECT_KEY,
            form_oid=TARGET_FORM_OID,
            visit_oid=TARGET_VISIT_OID,
            site_oid=TARGET_SITE_OID, # May or may not be required by the API/SDK
            data=NEW_RECORD_DATA
        )

        if created_record:
            # Adjust attribute access based on the actual SDK response model
            record_id = created_record.get('id', 'N/A') # Or created_record.id
            logging.info(f"Successfully created new record with ID: {record_id}")
            logging.debug(f"Created record details: {created_record}")
        else:
            # This case might indicate an issue if the SDK doesn't raise an exception on failure
            logging.error("Record creation call completed but did not return a record object. Check API logs or SDK behavior.")

    except ImednetException as e:
        # Specific API errors (e.g., validation errors, missing data, permissions)
        logging.error(f"An API error occurred during record creation: {e}")
        # You might want to inspect e.status_code or e.details if available
        # For example: if e.status_code == 400: logging.error("Bad request - check data format or required fields.")
    except AttributeError as e:
        logging.error(f"An SDK structure error occurred (e.g., client.records.create method or parameters might be incorrect): {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
