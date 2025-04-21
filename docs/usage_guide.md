# iMednet Python SDK Usage Guide

This guide provides instructions and examples on how to use the `imednet-python-sdk` to interact with the iMednet REST API.

## Installation

Install the SDK using pip. If installing from a local clone for development:

```bash
# Navigate to the repository root
pip install -e .
```

For production use, once published, you would typically install using:

```bash
pip install imednet-python-sdk
```

*(Adjust package name if different upon release)*

## Authentication & Initialization

The `ImednetClient` is the main entry point for interacting with the API. You need your iMednet API Key and Security Key to authenticate.

You can provide these keys directly when initializing the client or set them as environment variables:

* `IMEDNET_API_KEY`
* `IMEDNET_SECURITY_KEY`

```python
import os
from imednet_sdk import ImednetClient
# from imednet_sdk.exceptions import ImednetException # Planned for future implementation

# Option 1: Initialize with keys directly
# client = ImednetClient(api_key="YOUR_API_KEY", security_key="YOUR_SECURITY_KEY")

# Option 2: Initialize using environment variables (Recommended)
# Ensure environment variables IMEDNET_API_KEY and IMEDNET_SECURITY_KEY are set
# export IMEDNET_API_KEY='your_api_key'
# export IMEDNET_SECURITY_KEY='your_security_key'

try:
    # Client will automatically read from environment variables if not provided here
    client = ImednetClient()
    print("Client initialized successfully.")

except ValueError as e:
    print(f"Error initializing client: {e}")
    # In future, catch specific AuthenticationError
except Exception as e:
    print(f"An unexpected error occurred during initialization: {e}")

```

The client also accepts optional parameters for configuration (see Advanced Configuration below).

## Accessing API Resources

The `ImednetClient` provides access to different API resources through dedicated client properties. These properties lazily initialize the specific resource clients.

Available resource clients:

* `client.studies`: For interacting with study endpoints.
* `client.sites`: For interacting with site endpoints.
* `client.subjects`: For interacting with subject endpoints.
* `client.records`: For interacting with record endpoints.
* `client.forms`: For interacting with form endpoints.
* `client.intervals`: For interacting with interval endpoints.
* `client.record_revisions`: For interacting with record revision endpoints.
* `client.variables`: For interacting with variable endpoints.
* `client.codings`: For interacting with coding endpoints.
* `client.users`: For interacting with user endpoints.
* `client.visits`: For interacting with visit endpoints.
* `client.jobs`: For checking the status of background jobs.

## Making Requests

Each resource client provides methods corresponding to the available API operations for that resource. Most `list_*` methods support standard iMednet API query parameters for pagination, sorting, and filtering.

### Listing Resources (GET)

**Example: Listing Studies**

```python
try:
    # List the first 5 studies, sorted by studyKey ascending
    studies_response = client.studies.list_studies(size=5, sort="studyKey,asc")

    print(f"Status: {studies_response.metadata.status}")
    print(f"Total Studies Found (in this page): {len(studies_response.data)}")
    print(f"Total Pages: {studies_response.pagination.total_pages}")

    if studies_response.data:
        print("\\nFirst few studies:")
        for study in studies_response.data:
            # Access data using Pydantic model attributes (snake_case)
            print(f"- Name: {study.study_name}, Key: {study.study_key}, ID: {study.study_id}")

        # Get the key for the next example
        first_study_key = studies_response.data[0].study_key
    else:
        print("No studies found.")
        first_study_key = None # Set a default if no studies found

except Exception as e: # Replace with ImednetException later
    print(f"Error fetching studies: {e}")
    first_study_key = "YOUR_STUDY_KEY" # Fallback for example purposes
```

**Example: Listing Sites for a Specific Study with Filtering**

```python
if first_study_key:
    try:
        # List sites for the first study found, filtering for a specific site name
        # Note: Filter syntax follows API documentation (e.g., 'fieldName==value')
        sites_response = client.sites.list_sites(
            study_key=first_study_key,
            filter='siteName=="Central Hospital"', # Example filter
            size=10
        )

        print(f"\\nSites for study '{first_study_key}' matching filter:")
        if sites_response.data:
            for site in sites_response.data:
                print(f"- Name: {site.site_name}, ID: {site.site_id}, Status: {site.site_enrollment_status}")
        else:
            print("No sites found matching the criteria.")

    except Exception as e: # Replace with ImednetException later
        print(f"Error fetching sites for study {first_study_key}: {e}")
else:
    print("\\nSkipping site listing as no study key was available.")
```

**Example: Listing Subjects**

```python
if first_study_key:
    try:
        # List subjects for the study
        subjects_response = client.subjects.list_subjects(study_key=first_study_key, size=5)

        print(f"\\nSubjects for study '{first_study_key}':")
        if subjects_response.data:
            for subject in subjects_response.data:
                print(f"- Subject Key: {subject.subject_key}, OID: {subject.subject_oid}, Status: {subject.subject_status}")
        else:
            print("No subjects found.")

    except Exception as e: # Replace with ImednetException later
        print(f"Error fetching subjects for study {first_study_key}: {e}")
```

### Creating Resources (POST)

**Example: Creating Records**

Creating records is an asynchronous operation. The POST request initiates a background job, and the response contains the status of that job initiation.

```python
from imednet_sdk.models import RecordPostItem # Import the model for creating records

if first_study_key:
    # Define the records to create using the RecordPostItem model
    # Field names should match the Pydantic model definition (snake_case)
    # The SDK handles mapping to API's camelCase where necessary via aliases
    records_to_create = [
        RecordPostItem(
            site_id=48, # Example Site ID
            subject_key="SUBJ-001", # Example Subject Key
            interval_name="Screening", # Example Interval Name
            form_name="Demographics", # Example Form Name
            record_data={"DM_BRTHDT": "1980-01-15", "DM_SEX": "M"} # Example record data
        ),
        # Add more RecordPostItem objects as needed
    ]

    try:
        print(f"\\nAttempting to create {len(records_to_create)} record(s) for study '{first_study_key}'...")
        # Use the records client's create_records method
        job_status = client.records.create_records(
            study_key=first_study_key,
            records=records_to_create,
            email_notify="user@example.com" # Optional: Email address for job notification
        )

        print("Record creation job initiated successfully:")
        print(f"- Batch ID: {job_status.batch_id}")
        print(f"- Status: {job_status.status}")
        print(f"- Message: {job_status.message}")

        # You can use the batch_id to check the job status later
        # batch_id = job_status.batch_id

    except Exception as e: # Replace with ImednetException later
        print(f"Error creating records: {e}")
```

**Example: Checking Job Status**

```python
# Assuming 'batch_id' was obtained from a previous POST request (like create_records)
# batch_id = "some_batch_id_from_post_response"
# if first_study_key and batch_id:
#     try:
#         print(f"\\nChecking status for job {batch_id} in study '{first_study_key}'...")
#         status = client.jobs.get_job_status(study_key=first_study_key, batch_id=batch_id)
#         print(f"- Status: {status.status}")
#         print(f"- Message: {status.message}")
#         # Potentially check status.progress, status.completion_date etc.
#     except Exception as e: # Replace with ImednetException later
#         print(f"Error checking job status: {e}")
```

## Handling Responses

The SDK uses Pydantic models (defined in `imednet_sdk/models/`) to parse and validate API responses.

* **List Responses:** For endpoints that return lists (like `list_studies`, `list_sites`), the response object is typically an `ApiResponse` model (defined in `imednet_sdk/models/_common.py`). This contains:
  * `data`: A list of Pydantic models representing the resources (e.g., `List[StudyModel]`, `List[SiteModel]`). Access fields using Python snake\_case (e.g., `study.study_name`).
  * `metadata`: Information about the request/response (status, timestamp, etc.).
  * `pagination`: Details about the current page, total pages, total elements, etc. (`PaginationInfo` model).
* **Single Resource/Job Responses:** For endpoints returning a single item or status (like `create_records` or `get_job_status`), the response is the corresponding Pydantic model directly (e.g., `JobStatusModel`).

Pydantic handles the conversion from the API's camelCase JSON fields to the SDK's snake\_case model attributes automatically based on field aliases defined in the models.

## Error Handling

Currently, the SDK relies on `httpx` exceptions (`httpx.HTTPStatusError` for non-2xx responses, `httpx.RequestError` for connection issues).

A future task (Task 06) involves implementing custom exceptions (e.g., `ImednetException`, `AuthenticationError`, `APIError`) for more specific error handling. You should wrap API calls in `try...except` blocks to handle potential errors.

## Advanced Configuration

You can configure the client's behavior during initialization:

```python
import httpx

client = ImednetClient(
    # api_key="...", security_key="...",
    base_url="https://your-imednet-instance.imednet.com", # Optional: Override default production URL
    timeout=httpx.Timeout(60.0, connect=10.0), # Optional: Set timeouts (total, connect)
    retries=5, # Optional: Number of retries on transient errors (default: 3)
    backoff_factor=1.0, # Optional: Controls delay between retries (default: 0.5)
    # Optional: Customize which status codes, methods, or exceptions trigger retries
    # retry_statuses={500, 502, 503, 504, 429},
    # retry_methods={"GET", "POST", "PUT", "DELETE"},
    # retry_exceptions={httpx.ConnectError, httpx.ReadTimeout}
)
```

## Context Manager Usage

The `ImednetClient` supports the context manager protocol (`with` statement), which ensures the underlying HTTP connection pool is properly closed. This is the recommended way to use the client.

```python
import os
from imednet_sdk import ImednetClient

# Ensure environment variables are set or provide keys directly
try:
    with ImednetClient() as client:
        print("Using client within a context manager...")

        # Example: List studies
        studies_response = client.studies.list_studies(size=2)
        if studies_response.data:
            print("Studies found:")
            for study in studies_response.data:
                print(f"- {study.study_name}")
        else:
            print("No studies found.")

        # Add more API calls here...

    print("Client context manager finished, resources cleaned up.")

except ValueError as e:
    print(f"Error initializing client: {e}")
except Exception as e: # Replace with ImednetException later
    print(f"An error occurred: {e}")

```

This guide covers the fundamental usage patterns. Refer to the specific resource client methods and Pydantic models for details on available operations and data structures. Consult the official iMednet API documentation for comprehensive details on endpoints, parameters, and filtering syntax.
