.. _usage-pagination:

Handling Pagination
===================

Many iMednet API endpoints that return lists of resources use pagination to manage potentially large datasets. The SDK provides ways to handle these paginated responses.

Pagination Parameters
---------------------

Most ``list_*`` methods accept the following query parameters to control pagination:

* ``page`` (int): The page number to retrieve (1-based index). Defaults to 1.
* ``size`` (int): The number of items per page. Defaults to a value set by the API (often 20 or 50), with a maximum limit (often 100 or 200).

.. code-block:: python

   # Get the second page of studies, with 10 items per page
   response = client.studies.list_studies(page=2, size=10)

Response Metadata
-----------------

List responses include a ``metadata`` attribute containing pagination details:

* ``metadata.page`` (int): The current page number.
* ``metadata.size`` (int): The number of items requested per page.
* ``metadata.total_count`` (int): The total number of resources available across all pages.
* ``metadata.total_pages`` (int): The total number of pages available.

.. code-block:: python

   response = client.records.list_records(study_key="STUDY123", size=50)

   print(f"Current Page: {response.metadata.page}")
   print(f"Page Size: {response.metadata.size}")
   print(f"Total Records: {response.metadata.total_count}")
   print(f"Total Pages: {response.metadata.total_pages}")

Manual Pagination
-----------------

You can fetch all resources by manually iterating through the pages until you have retrieved all items.

**Example: Fetching all sites for a study**

.. code-block:: python

   from imednet_sdk import ImednetClient
   from imednet_sdk.exceptions import ImednetException

   study_key_to_query = "STUDY123"
   all_sites = []
   current_page = 1
   page_size = 100 # Request max allowed size to minimize requests

   try:
       with ImednetClient() as client:
           while True:
               print(f"Fetching page {current_page}...")
               response = client.sites.list_sites(
                   study_key=study_key_to_query,
                   page=current_page,
                   size=page_size
               )

               if response.data:
                   all_sites.extend(response.data)
                   print(f"  -> Retrieved {len(response.data)} sites. Total so far: {len(all_sites)}")
               else:
                   print("  -> No more sites found on this page.")

               # Check if this was the last page
               if current_page >= response.metadata.total_pages:
                   print("Reached the last page.")
                   break

               # Move to the next page
               current_page += 1

           print(f"\nFinished fetching. Total sites retrieved: {len(all_sites)}")

   except ImednetException as e:
       print(f"API Error: {e.status_code} - {e.detail}")
   except Exception as e:
       print(f"An unexpected error occurred: {e}")


Automatic Iteration (Planned)
-----------------------------

.. note::
   Helper functions or iterators to automatically handle pagination across all resources are planned for a future version (related to Task 11: Pagination and Iterators). This will simplify the process of retrieving all items from a paginated endpoint.
