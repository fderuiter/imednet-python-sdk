Quickstart
==========

This guide provides a basic example of how to use the `imednet-python-sdk`.

**1. Import the Client**

First, import the main client class:

.. code-block:: python

   from imednet_sdk import IMednetClient

**2. Initialize the Client**

You'll need your API credentials (e.g., API key, base URL) to initialize the client. The exact authentication method will be detailed later, but conceptually:

.. code-block:: python

   # Replace with actual configuration/authentication details
   api_base_url = "https://api.imednet.com/v1" # Example URL
   api_key = "YOUR_API_KEY"

   client = IMednetClient(base_url=api_base_url, api_key=api_key)

**3. Make an API Call**

Once the client is initialized, you can access different API resources. For example, to list studies (assuming a `list_studies` method exists):

.. code-block:: python

   try:
       studies = client.studies.list()
       for study in studies:
           print(f"Study ID: {study.id}, Name: {study.name}") # Access model attributes
   except Exception as e:
       print(f"An error occurred: {e}")

This example demonstrates the basic workflow: initialize the client and call methods corresponding to API endpoints. The SDK handles request construction, authentication, and response parsing into Pydantic models.

Refer to the :doc:`api` reference for details on available methods and models.
