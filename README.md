# imednet-python-sdk

## Overview

The imednet-python-sdk is a Python Software Development Kit (SDK) designed to provide a simple and efficient interface for interacting with the iMednet REST API. This SDK abstracts the complexities of making HTTP requests and handling responses, allowing developers to focus on building applications without worrying about the underlying API details.

## Vision Statement

The vision of the imednet-python-sdk is to empower developers by providing a robust and user-friendly SDK that simplifies the integration with the iMednet REST API. Our goal is to enhance productivity, reduce development time, and improve the overall developer experience when working with iMednet services.

## Current Status (As of April 21, 2025)

Development is actively progressing. The core client functionality is implemented, along with Pydantic models for data handling and clients for several key API endpoints (see Features below). Testing infrastructure is in place.

## Features

* **Core HTTP Client:** Robust client based on `httpx` handling authentication, base URL configuration, timeouts, retries, and context management (`with` statement).
* **Authentication:** Handles API Key and Security Key via constructor arguments or environment variables (`IMEDNET_API_KEY`, `IMEDNET_SECURITY_KEY`).
* **Data Modeling:** Uses Pydantic v2+ models for request/response data validation and serialization/deserialization.
* **Resource Clients:** Provides dedicated clients for interacting with specific API resources, accessible via the main client instance (e.g., `client.studies`). Implemented endpoints include:
  * Studies: `list_studies`
  * Sites: `list_sites`
  * Forms: `list_forms`
  * Intervals: `list_intervals`
  * Records: `list_records`, `create_records`
  * Record Revisions: `list_record_revisions`
  * Variables: `list_variables`
  * Codings: `list_codings`
  * Subjects: `list_subjects`
  * Users: `list_users`
  * Visits: `list_visits`
  * Jobs: `get_job_status`
* **Error Handling:** Basic error handling for HTTP status codes and connection issues (further refinement planned).
* **Pagination & Filtering:** Supports standard API query parameters for pagination, sorting, and filtering where applicable.

## Installation

**(Note: The package is not yet published on PyPI.)**

Once published, you can install the imednet-python-sdk using pip:

```bash
pip install imednet-python-sdk
```

Currently, you can install it directly from the source code:

```bash
# Install from the local clone
pip install .

# Or install in editable mode for development (requires cloning the repo first)
# git clone https://github.com/yourusername/imednet-python-sdk.git
# cd imednet-python-sdk
pip install -e .[dev]
```

*(Note: Assumes `[dev]` extra is defined in `pyproject.toml`)*

## Authentication

The SDK requires your iMednet API Key and Security Key for authentication. You can provide these credentials in two ways:

1. **Directly during client initialization:**

   ```python
   from imednet_sdk import ImednetClient

   client = ImednetClient(
       api_key='YOUR_API_KEY',
       security_key='YOUR_SECURITY_KEY'
   )
   ```

2. **Via environment variables:**

   Set the following environment variables:

   * `IMEDNET_API_KEY`
   * `IMEDNET_SECURITY_KEY`

   The client will automatically pick them up if not provided during initialization:

   ```python
   # Example for bash/zsh
   # export IMEDNET_API_KEY='your_api_key'
   # export IMEDNET_SECURITY_KEY='your_security_key'

   # Example for PowerShell
   # $env:IMEDNET_API_KEY='your_api_key'
   # $env:IMEDNET_SECURITY_KEY='your_security_key'

   from imednet_sdk import ImednetClient

   # Client automatically uses environment variables
   client = ImednetClient()
   ```

## Usage

Here is a simple example of how to use the SDK:

```python
import os
from imednet_sdk import ImednetClient
from imednet_sdk.exceptions import ImednetException # Assuming defined in Task 6

# Credentials can be passed directly or set as environment variables
# export IMEDNET_API_KEY='your_api_key'
# export IMEDNET_SECURITY_KEY='your_security_key'

try:
    # Initialize the client (reads from env vars if not provided)
    client = ImednetClient()

    # Example: List studies
    print("Fetching studies...")
    studies_response = client.studies.list_studies(size=5) # Get first 5 studies

    print(f"Metadata: {studies_response.metadata}")
    if studies_response.data:
        print("Studies found:")
        for study in studies_response.data:
            print(f"- {study.study_name} (Key: {study.study_key}, Status: {study.status})")
    else:
        print("No studies found.")

    # Example: List sites for a specific study (replace 'YOUR_STUDY_KEY')
    study_key_to_query = 'YOUR_STUDY_KEY' # Replace with a valid key
    if studies_response.data: # Use the key from the first study found if available
        study_key_to_query = studies_response.data[0].study_key

    print(f"\nFetching sites for study {study_key_to_query}...")
    sites_response = client.sites.list_sites(study_key=study_key_to_query, size=5)

    print(f"Metadata: {sites_response.metadata}")
    if sites_response.data:
        print("Sites found:")
        for site in sites_response.data:
             print(f"- {site.site_name} (Key: {site.site_key})")
    else:
        print(f"No sites found for study {study_key_to_query}.")

except ImednetException as e:
    print(f"An API error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    # Although httpx client is managed internally, explicit close is good practice if not using 'with'
    # If using 'with ImednetClient() as client:', close is handled automatically.
    # client.close() # Or implement close if needed, httpx handles it with context manager
    pass

```

*(Note: The `ImednetException` is planned for Task 6, adjust exception handling as needed)*

## Documentation

Comprehensive documentation, including API reference and usage guides, is generated using Sphinx.

* **View the Documentation:** [Link to hosted documentation or local build path] (e.g., `docs/build/html/index.html` after building)
  * To build the documentation locally, navigate to the `docs/source` directory and run `make html` (or `sphinx-build -b html . ../build/html` on Windows without Make). You need to have Sphinx and the required extensions installed (`pip install -r requirements-dev.txt`).

For project-related documents, see:

* [Vision Statement](docs/project/vision.md)
* [Detailed Design](docs/project/design.md)
* [High-Level Architecture](docs/project/architecture.md)
* [System Context Diagram](docs/project/context_diagram.md)
* [Coding Standards](docs/coding_standards.md)

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes. Ensure adherence to [Coding Standards](docs/coding_standards.md).

## License

This project is licensed under the MIT License. See the `LICENSE` file (if created) or `pyproject.toml` for more details.
