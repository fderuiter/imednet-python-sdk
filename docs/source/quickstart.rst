.. _quickstart:

Quickstart
==========

This guide provides a basic example of how to get started with the `imednet-python-sdk`.

**1. Installation**

Install the SDK using pip. For development, install with the `[dev]` extras:

.. code-block:: bash

   # From PyPI (once published)
   # pip install imednet-python-sdk

   # Locally for development
   pip install -e .[dev]

Refer to the :doc:`installation` guide for more details.

**2. Credentials**

The SDK requires an API Key and a Security Key for authentication. You can provide these either during client initialization or by setting the following environment variables:

*   `IMEDNET_API_KEY`
*   `IMEDNET_SECURITY_KEY`

**3. Initialize the Client**

Import and initialize the main client class. If credentials are not passed directly, the client will attempt to read them from environment variables.

.. code-block:: python

   import os
   from imednet_sdk import ImednetClient
   # from imednet_sdk.exceptions import ImednetException # Import specific exceptions when available

   # Option 1: Initialize with environment variables (Recommended)
   # Ensure IMEDNET_API_KEY and IMEDNET_SECURITY_KEY are set in your environment
   try:
       client = ImednetClient()
       print("Client initialized successfully using environment variables.")
   except ValueError as e: # Catches missing credentials error for now
       print(f"Error initializing client: {e}")
       print("Please ensure IMEDNET_API_KEY and IMEDNET_SECURITY_KEY environment variables are set.")
       # Exit or handle error appropriately
       exit()

   # Option 2: Initialize with direct arguments (Less Recommended for production)
   # api_key = "YOUR_API_KEY"
   # security_key = "YOUR_SECURITY_KEY"
   # base_url = "https://your-imednet-instance.com/api" # Optional: Override base URL
   # try:
   #     client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
   #     print("Client initialized successfully using direct arguments.")
   # except ValueError as e:
   #     print(f"Error initializing client: {e}")
   #     exit()


**4. Make an API Call**

Once the client is initialized, you can access different API resource clients (e.g., `studies`, `sites`) and call their methods. The SDK handles request construction, authentication, and response parsing into Pydantic models.

.. code-block:: python

   try:
       print("\nFetching the first 5 studies...")
       # Access the 'studies' resource client and call 'list_studies'
       # Pass parameters like 'size' for pagination
       studies_response = client.studies.list_studies(size=5)

       # Responses are typically wrapped in ApiResponseModel
       print(f"Total studies found (metadata): {studies_response.metadata.pagination.total}")

       if studies_response.data:
           print("Studies:")
           # Access the list of study models from the 'data' attribute
           for study in studies_response.data:
               # Access attributes of the Pydantic model (e.g., StudyModel)
               print(f"- ID: {study.study_key}, Name: {study.study_name}, Status: {study.status}")
       else:
           print("No studies found.")

   # except ImednetException as e: # Use specific SDK exceptions when available (Task 6)
   #     print(f"An API error occurred: {e}")
   except Exception as e:
       print(f"An unexpected error occurred: {e}")

   # The client uses httpx internally, which should be closed.
   # Using the client as a context manager is recommended:
   # with ImednetClient() as client:
   #    # ... make calls ...
   # client.close() # Or call close() explicitly if not using 'with'

This example demonstrates the basic workflow. Refer to the :doc:`api/index` reference and the more detailed `docs/usage_guide.md` for available methods, models, and advanced usage patterns.
