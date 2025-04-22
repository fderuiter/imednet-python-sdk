.. _usage-filtering-sorting:

Filtering and Sorting
=====================

Many iMednet API endpoints allow you to filter and sort the results when listing resources. The SDK exposes these capabilities through keyword arguments in the ``list_*`` methods.

Filtering
---------

Filtering allows you to retrieve only the resources that match specific criteria. The available filter parameters vary depending on the API endpoint.

**Common Filter Parameters:**

*   ``study_key``: Often required when listing resources within a specific study (e.g., sites, subjects, records).
*   Status fields (e.g., ``status``, ``subject_status``): Filter by the current status of the resource.
*   Date/Time fields: Filter based on creation or modification timestamps (exact parameter names may vary).
*   Specific identifiers (e.g., ``subject_key``, ``form_key``): Filter related resources.

**Passing Filters:**

You pass filter criteria as keyword arguments directly to the ``list_*`` method.

**Example: Finding Subjects with a Specific Status**

.. code-block:: python

   from imednet_sdk import ImednetClient
   from imednet_sdk.exceptions import ImednetException

   study_key_to_query = "STUDY123"
   target_status = "Screened" # Example status

   try:
       with ImednetClient() as client:
           print(f"Finding subjects with status '{target_status}' in study '{study_key_to_query}'...")
           response = client.subjects.list_subjects(
               study_key=study_key_to_query,
               subject_status=target_status, # Pass the status as a filter
               size=50 # Optional: adjust page size
           )

           print(f"Found {response.metadata.total_count} subjects with status '{target_status}'.")
           if response.data:
               print("\nFirst few matching subjects:")
               for subject in response.data:
                   print(f"- Subject Key: {subject.subject_key}, Status: {subject.subject_status}")

   except ImednetException as e:
       print(f"API Error: {e.status_code} - {e.detail}")
   except Exception as e:
       print(f"An unexpected error occurred: {e}")

.. note::
   Refer to the specific iMednet API documentation or the SDK's method docstrings (once available/updated) for the exact filter parameters supported by each endpoint.

Sorting
-------

Sorting allows you to control the order in which resources are returned.

**Sort Parameter:**

The ``sort`` parameter is commonly used to specify the field to sort by and the direction (ascending or descending).

*   The format is typically ``field_name`` for ascending order or ``-field_name`` for descending order.
*   Multiple sort fields might be supported, separated by commas (e.g., ``sort="status,-created_at"``).

**Example: Listing Studies Sorted by Name (Ascending)**

.. code-block:: python

   # Assuming 'client' is an initialized ImednetClient

   try:
       response = client.studies.list_studies(
           sort="study_name", # Sort by study_name ascending
           size=10
       )

       print("Studies sorted by name (A-Z):")
       for study in response.data:
           print(f"- {study.study_name}")

   except ImednetException as e:
       print(f"API Error: {e.status_code} - {e.detail}")

**Example: Listing Records Sorted by Creation Date (Descending)**

.. code-block:: python

   # Assuming 'client' and 'study_key' are defined

   try:
       response = client.records.list_records(
           study_key=study_key_to_query,
           sort="-created_at", # Sort by creation date, newest first
           size=10
       )

       print("\nMost recently created records:")
       for record in response.data:
           print(f"- Record Key: {record.record_key}, Created: {record.created_at}")

   except ImednetException as e:
       print(f"API Error: {e.status_code} - {e.detail}")

.. note::
   The specific fields available for sorting depend on the API endpoint. Consult the iMednet API documentation for details.
