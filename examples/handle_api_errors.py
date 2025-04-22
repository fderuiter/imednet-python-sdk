# examples/handle_api_errors.py
"""
Example: Handling API Errors with iMednet Python SDK.

This script demonstrates how to gracefully handle various exceptions that might
be raised by the `imednet-python-sdk` when interacting with the iMednet API.
It covers common scenarios like authentication failures, resource not found errors,
validation errors, and general API exceptions.

**Prerequisites:**

1.  **Install SDK:** `pip install imednet-sdk python-dotenv`
2.  **Environment Variables:** Create a `.env` file in the same directory
    with your iMednet API key, security key, and base URL:
    ```
    IMEDNET_API_KEY="your_api_key_here"
    IMEDNET_SECURITY_KEY="your_security_key_here"
    IMEDNET_BASE_URL="https://your_imednet_instance.imednetapi.com"
    ```
3.  **Configuration:** Review the `INVALID_API_KEY`, `INVALID_SECURITY_KEY`,
    `NON_EXISTENT_STUDY_KEY`, and `VALID_STUDY_KEY` constants below. You might
    need to replace `VALID_STUDY_KEY` with an actual key from your instance
    for the general error test.

**Usage:**

```bash
python examples/handle_api_errors.py
```

The script will run through several test cases designed to trigger specific
API errors and log how they are caught and handled.
"""

import logging
import os

from dotenv import load_dotenv
from pydantic_core import ValidationError

from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import (
    AuthenticationError,
    BadRequestError,
    ImednetSdkException,
    NotFoundError,
    RateLimitError,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")  # Added security key
BASE_URL = os.getenv("IMEDNET_BASE_URL")

# --- Configuration for Test Cases ---
# Use deliberately incorrect values to trigger specific errors
INVALID_API_KEY = "invalid-api-key-123"
INVALID_SECURITY_KEY = "invalid-security-key-abc"
NON_EXISTENT_STUDY_KEY = "STUDY_DOES_NOT_EXIST_KEY"
VALID_STUDY_KEY = "DEMO"  # Replace with a VALID Study Key if needed for other tests
# -----------------------------------


def main():
    """Runs different test cases to demonstrate SDK error handling."""
    if not BASE_URL:
        logging.error("Base URL not configured. Set IMEDNET_BASE_URL environment variable.")
        return

    # --- Test Case 1: Authentication Error (Invalid API Key) ---
    logging.info("--- Test Case 1: Authentication Error (Invalid API Key) ---")
    try:
        logging.info(f"Initializing client with INVALID API Key: {INVALID_API_KEY}")
        # Use a valid security key for this test to isolate the API key issue
        invalid_client = ImednetClient(
            base_url=BASE_URL, api_key=INVALID_API_KEY, security_key=SECURITY_KEY
        )
        logging.info("Attempting to list studies (expected to fail with 401)...")
        # Any authenticated call should fail
        invalid_client.studies.list_studies(size=1)
        assert False, (
            "Authentication error was expected but not caught. " "Check SDK behavior or test setup."
        )
    except AuthenticationError as e:
        logging.error(f"Caught expected AuthenticationError: {e}")
        logging.error(
            f"  Status Code: {e.status_code}, API Code: {e.api_error_code}, "
            f"Details: {e.response_body}"
        )
    except ImednetSdkException as e:
        logging.error(f"Caught a general ImednetSdkException (unexpected for auth test 1): {e}")
    except Exception as e:
        logging.error(f"Caught an unexpected non-SDK error: {e}", exc_info=True)

    # --- Test Case 1b: Authentication Error (Invalid Security Key) ---
    logging.info("\n--- Test Case 1b: Authentication Error (Invalid Security Key) ---")
    if not API_KEY:
        logging.warning("Skipping Auth Test 1b: Valid API Key (IMEDNET_API_KEY) not set.")
    else:
        try:
            logging.info(f"Initializing client with INVALID Security Key: {INVALID_SECURITY_KEY}")
            invalid_client = ImednetClient(
                base_url=BASE_URL, api_key=API_KEY, security_key=INVALID_SECURITY_KEY
            )
            logging.info("Attempting to list studies (expected to fail with 401)...")
            invalid_client.studies.list_studies(size=1)
            logging.warning(
                "Authentication error was expected but not caught. Check SDK behavior/test setup."
            )
        except AuthenticationError as e:
            logging.error(f"Caught expected AuthenticationError: {e}")
            logging.error(
                f"  Status Code: {e.status_code}, API Code: {e.api_error_code}, "
                f"Details: {e.response_body}"
            )
        except ImednetSdkException as e:
            logging.error(
                f"Caught a general ImednetSdkException (unexpected for auth test 1b): {e}"
            )
        except Exception as e:
            logging.error(f"Caught an unexpected non-SDK error: {e}", exc_info=True)

    # --- Test Case 2: Not Found Error ---
    logging.info("\n--- Test Case 2: Not Found Error ---")
    if not API_KEY or not SECURITY_KEY:
        logging.warning("Skipping Not Found test: Valid API Key or Security Key not set.")
    else:
        try:
            client = ImednetClient(base_url=BASE_URL)  # Uses env vars
            logging.info("Client initialized with valid credentials.")
            logging.info(
                f"Attempting to list sites for non-existent study: {NON_EXISTENT_STUDY_KEY}"
            )
            # Use a valid method but with a key that likely doesn't exist
            client.sites.list_sites(study_key=NON_EXISTENT_STUDY_KEY, size=1)
            logging.warning(
                "Not Found error was expected but not caught. Check SDK behavior or Key."
            )
        except NotFoundError as e:
            logging.error(f"Caught expected NotFoundError: {e}")
            logging.error(
                f"  Status Code: {e.status_code}, API Code: {e.api_error_code}, "
                f"Details: {e.response_body}"
            )
        except AuthenticationError as e:  # Catch auth error here too, in case credentials are bad
            logging.error(f"Caught AuthenticationError unexpectedly during Not Found test: {e}")
        except ImednetSdkException as e:
            logging.error(f"Caught a general ImednetSdkException (unexpected for not found): {e}")
        except Exception as e:
            logging.error(f"Caught an unexpected non-SDK error: {e}", exc_info=True)

    # --- Test Case 3: Bad Request / Validation Error (Example: Invalid Page Number) ---
    logging.info("\n--- Test Case 3: Bad Request / Validation Error (Invalid Page Number) ---")
    if not API_KEY or not SECURITY_KEY:
        logging.warning("Skipping Bad Request test: Valid API Key or Security Key not set.")
    elif VALID_STUDY_KEY == "DEMO" and not os.getenv(
        "RUN_DEMO_TESTS"
    ):  # Avoid running potentially failing tests on DEMO by default
        logging.warning(
            "Skipping Bad Request test on DEMO study. Set RUN_DEMO_TESTS env var to run."
        )
    else:
        try:
            client = ImednetClient(base_url=BASE_URL)
            logging.info("Client initialized with valid credentials.")
            invalid_page = -1  # Page number must be non-negative
            logging.info(
                f"Attempting to list sites for study '{VALID_STUDY_KEY}' "
                f"with invalid page number: {invalid_page}"
            )
            client.sites.list_sites(study_key=VALID_STUDY_KEY, page=invalid_page, size=1)
            logging.warning(
                "Bad Request or Validation error was expected but not caught. "
                "Check SDK or parameter validation."
            )

        # Catch specific validation error if distinguished by the SDK (e.g., based on API code 1000)
        except ValidationError as e:
            logging.error(f"Caught expected ValidationError: {e}")
            logging.error(
                f"  Status Code: {e.status_code}, API Code: {e.api_error_code}, "
                f"Details: {e.response_body}"
            )
        # Catch general bad request error
        except BadRequestError as e:
            logging.error(f"Caught expected BadRequestError: {e}")
            logging.error(
                f"  Status Code: {e.status_code}, API Code: {e.api_error_code}, "
                f"Details: {e.response_body}"
            )
        except NotFoundError as e:  # If the VALID_STUDY_KEY was actually invalid
            logging.error(f"Caught NotFoundError unexpectedly during Bad Request test: {e}")
        except AuthenticationError as e:
            logging.error(f"Caught AuthenticationError unexpectedly during Bad Request test: {e}")
        except ImednetSdkException as e:
            logging.error(f"Caught a general ImednetSdkException: {e}")
        except Exception as e:
            logging.error(f"Caught an unexpected non-SDK error: {e}", exc_info=True)

    # --- Test Case 4: General Successful Call (Example: Listing Studies) ---
    logging.info("\n--- Test Case 4: General Successful Call Handling ---")
    if not API_KEY or not SECURITY_KEY:
        logging.warning("Skipping Successful Call test: Valid API Key or Security Key not set.")
    else:
        try:
            client = ImednetClient(base_url=BASE_URL)
            logging.info("Client initialized with valid credentials.")
            logging.info("Attempting to list studies...")
            response = client.studies.list_studies(size=5)
            if response and response.data:
                logging.info(
                    f"Successfully listed {len(response.data)} studies (up to 5). "
                    f"First study key: {response.data[0].studyKey}"
                )
            else:
                logging.info("Successfully called list_studies, but no studies were returned.")

        # Catch specific errors first
        except RateLimitError as e:
            logging.error(f"Caught RateLimitError during successful call test: {e}. Please wait.")
        except AuthenticationError as e:
            logging.error(
                f"Caught AuthenticationError unexpectedly during successful call test: {e}"
            )
        # Catch the base SDK exception
        except ImednetSdkException as e:
            logging.error(
                f"Caught an unexpected ImednetSdkException during successful call test: {e}"
            )
            logging.error(
                f"  Status Code: {e.status_code}, API Code: {e.api_error_code}, "
                f"Details: {e.response_body}"
            )
        except Exception as e:
            logging.error(
                f"Caught an unexpected non-SDK error during successful call test: {e}",
                exc_info=True,
            )


if __name__ == "__main__":
    main()
