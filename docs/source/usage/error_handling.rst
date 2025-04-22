.. _usage-error-handling:

Error Handling
==============

When interacting with the iMednet API via the SDK, various issues can occur, such as network problems, invalid requests, or server-side errors. The SDK provides mechanisms to handle these situations gracefully.

SDK Exceptions
--------------

The primary exception raised by the SDK for API-related errors is :class:`~imednet_sdk.exceptions.ImednetException`. This exception class serves as a base for more specific HTTP error exceptions.

**Key Attributes of `ImednetException`:**

*   ``status_code`` (int): The HTTP status code returned by the API (e.g., 400, 401, 404, 500).
*   ``detail`` (str | dict | None): The error message or details provided in the API response body. This can be a simple string or a structured dictionary depending on the error.
*   ``request`` (httpx.Request | None): The original request object that led to the error.
*   ``response`` (httpx.Response | None): The full response object received from the API.

**Specific HTTP Error Exceptions:**

The SDK defines subclasses of `ImednetException` for common HTTP error codes, allowing for more granular error handling:

*   :class:`~imednet_sdk.exceptions.BadRequestError` (400)
*   :class:`~imednet_sdk.exceptions.AuthenticationError` (401)
*   :class:`~imednet_sdk.exceptions.ForbiddenError` (403)
*   :class:`~imednet_sdk.exceptions.NotFoundError` (404)
*   :class:`~imednet_sdk.exceptions.ConflictError` (409)
*   :class:`~imednet_sdk.exceptions.UnprocessableEntityError` (422)
*   :class:`~imednet_sdk.exceptions.InternalServerError` (500)
*   ... and potentially others for different 4xx/5xx codes.

Catching Exceptions
-------------------

Use standard Python ``try...except`` blocks to catch potential errors.

**Catching General API Errors:**

You can catch the base :class:`~imednet_sdk.exceptions.ImednetException` to handle any error originating from the API interaction.

.. code-block:: python

   from imednet_sdk import ImednetClient
   from imednet_sdk.exceptions import ImednetException

   try:
       with ImednetClient() as client:
           # Attempt an API call that might fail
           response = client.studies.list_studies(size=9999) # Invalid size might cause an error
           # ... process response ...

   except ImednetException as e:
       print(f"An API error occurred!")
       print(f"Status Code: {e.status_code}")
       print(f"Details: {e.detail}")
       # Log the error, notify user, etc.

   except Exception as e:
       # Catch any other unexpected errors (network issues, SDK bugs, etc.)
       print(f"An unexpected error occurred: {e}")

**Catching Specific HTTP Errors:**

For more specific handling, catch the relevant subclass. This is useful for differentiating between, for example, a resource not being found (404) and an authentication failure (401).

.. code-block:: python

   from imednet_sdk import ImednetClient
   from imednet_sdk.exceptions import NotFoundError, AuthenticationError, ImednetException

   study_key_to_get = "STUDY_DOES_NOT_EXIST"

   try:
       with ImednetClient() as client: # Assuming potentially bad credentials
           study = client.studies.get_study(study_key=study_key_to_get)
           print(f"Found study: {study.study_name}")

   except NotFoundError as e:
       print(f"Error: Study with key '{study_key_to_get}' was not found.")
       print(f"Details from API: {e.detail}")

   except AuthenticationError as e:
       print(f"Error: Authentication failed. Check your API Key and Security Key.")
       print(f"Details from API: {e.detail}")

   except ImednetException as e:
       # Catch any other API errors not specifically handled above
       print(f"An unexpected API error occurred: {e.status_code} - {e.detail}")

   except Exception as e:
       print(f"An unexpected non-API error occurred: {e}")

Network Errors
--------------

Network-related issues (e.g., connection timeouts, DNS errors) are typically raised as exceptions from the underlying HTTP library (`httpx`). You might want to catch `httpx.RequestError` or its subclasses if you need to handle these specifically, although often catching the generic `Exception` is sufficient for logging or reporting unexpected failures.

.. code-block:: python

   import httpx
   # ... other imports ...

   try:
       # ... API call ...
   except ImednetException as e:
       # ... handle API errors ...
   except httpx.TimeoutException:
       print("Error: The request to the iMednet API timed out.")
   except httpx.RequestError as e:
       print(f"Error: A network issue occurred: {e}")
   except Exception as e:
       print(f"An unexpected error occurred: {e}")
