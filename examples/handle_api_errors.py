# examples/handle_api_errors.py
"""
Example script demonstrating how to handle potential API errors and exceptions
when using the iMednet Python SDK.
"""
import os
import logging
from dotenv import load_dotenv
from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import ImednetException, AuthenticationError, NotFoundError, RateLimitError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")

# --- Configuration for Test Cases ---
# Use deliberately incorrect values to trigger specific errors
INVALID_API_KEY = "invalid-api-key-123"
NON_EXISTENT_STUDY_OID = "STUDY_DOES_NOT_EXIST_OID"
VALID_STUDY_OID = "STUDY_OID_HERE" # Replace with a VALID Study OID if needed for other tests
# -----------------------------------

def main():
    """Main function to demonstrate error handling."""
    if not BASE_URL:
        logging.error("Base URL not configured. Set IMEDNET_BASE_URL environment variable.")
        return

    # --- Test Case 1: Authentication Error ---
    logging.info("--- Test Case 1: Authentication Error ---")
    try:
        logging.info(f"Initializing client with INVALID API Key: {INVALID_API_KEY}")
        invalid_client = ImednetClient(base_url=BASE_URL, api_key=INVALID_API_KEY)
        # Attempt an API call that requires authentication
        logging.info("Attempting to list studies (expected to fail)...")
        invalid_client.studies.list() # This call should trigger the error
        logging.warning("Authentication error was expected but not caught. Check SDK behavior.")
    except AuthenticationError as e:
        logging.error(f"Caught expected AuthenticationError: {e}")
        # Specific handling for authentication issues (e.g., prompt user to check credentials)
    except ImednetException as e:
        logging.error(f"Caught a general ImednetException (unexpected for auth): {e}")
    except Exception as e:
        logging.error(f"Caught an unexpected non-SDK error: {e}")

    # --- Test Case 2: Not Found Error ---
    logging.info("\n--- Test Case 2: Not Found Error ---")
    if not API_KEY:
        logging.warning("Skipping Not Found test: Valid API Key (IMEDNET_API_KEY) not set.")
    else:
        try:
            client = ImednetClient(base_url=BASE_URL, api_key=API_KEY)
            logging.info("Client initialized with valid API Key.")
            logging.info(f"Attempting to get details for non-existent study: {NON_EXISTENT_STUDY_OID}")
            # Assumes client.studies.get() exists and takes study_oid
            client.studies.get(study_oid=NON_EXISTENT_STUDY_OID) # This call should trigger the error
            logging.warning("Not Found error was expected but not caught. Check SDK behavior or OID.")
        except NotFoundError as e:
            logging.error(f"Caught expected NotFoundError: {e}")
            # Specific handling for resource not found (e.g., inform user the OID is invalid)
        except AuthenticationError as e: # Catch auth error here too, in case the valid key is actually invalid
             logging.error(f"Caught AuthenticationError unexpectedly during Not Found test: {e}")
        except ImednetException as e:
            logging.error(f"Caught a general ImednetException (unexpected for not found): {e}")
        except AttributeError as e:
             logging.error(f"SDK structure error: client.studies.get might not exist or takes different parameters. {e}")
        except Exception as e:
            logging.error(f"Caught an unexpected non-SDK error: {e}")

    # --- Test Case 3: General API Error Handling (Example: Listing Sites) ---
    logging.info("\n--- Test Case 3: General Error Handling ---")
    if not API_KEY:
        logging.warning("Skipping General Error test: Valid API Key (IMEDNET_API_KEY) not set.")
    elif VALID_STUDY_OID == "STUDY_OID_HERE":
         logging.warning("Skipping General Error test: Replace 'STUDY_OID_HERE' with a valid Study OID.")
    else:
        try:
            client = ImednetClient(base_url=BASE_URL, api_key=API_KEY)
            logging.info("Client initialized with valid API Key.")
            logging.info(f"Attempting to list sites for study: {VALID_STUDY_OID}")
            sites = client.sites.list(study_oid=VALID_STUDY_OID)
            logging.info(f"Successfully listed {len(sites)} sites for study {VALID_STUDY_OID}.")
            # Add more complex operations here that might fail

        # Catch more specific errors first if they exist in the SDK
        except RateLimitError as e:
             logging.error(f"Caught RateLimitError: {e}. Please wait before making more requests.")
        except NotFoundError as e: # e.g., if the VALID_STUDY_OID was actually invalid
             logging.error(f"Caught NotFoundError unexpectedly: {e}")
        except AuthenticationError as e:
             logging.error(f"Caught AuthenticationError unexpectedly: {e}")

        # Catch the base SDK exception for other API-related errors
        except ImednetException as e:
            logging.error(f"Caught a general ImednetException: {e}")
            # Inspect error details if available (e.g., e.status_code, e.response_text)
            # Example: if hasattr(e, 'status_code'): logging.error(f"  Status Code: {e.status_code}")

        # Catch potential SDK usage errors (e.g., wrong method name)
        except AttributeError as e:
             logging.error(f"SDK structure error: A method or attribute might be incorrect. {e}")

        # Catch any other unexpected errors
        except Exception as e:
            logging.error(f"Caught an unexpected non-SDK error: {e}")

if __name__ == "__main__":
    main()
