.. _usage-making-requests:

Making Requests
===============

Once the :class:`~imednet_sdk.client.ImednetClient` is initialized, you can interact with the iMednet API through its resource client attributes.

Accessing Resource Clients
--------------------------

The main client provides access to specific API resources through dedicated client attributes. For example:

* ``client.studies``: Access study-related endpoints.
* ``client.sites``: Access site-related endpoints.
* ``client.records``: Access record-related endpoints.
* ``client.subjects``: Access subject-related endpoints.

Refer to the :doc:`../api/api_endpoints` section for a full list of available resource clients.

Listing Resources
-----------------

Most resource clients provide a ``list_*`` method to retrieve a collection of resources. These methods typically accept pagination parameters like ``page`` and ``size`` (see :doc:`pagination`).

**Example: Listing Studies**

.. code-block:: python

   from imednet_sdk import ImednetClient
   from imednet_sdk.exceptions import ImednetException

   try:
       with ImednetClient() as client:
           # Get the first 5 studies
           studies_response = client.studies.list_studies(size=5)

           print(f"Total studies found: {studies_response.metadata.total_count}")
           print(f"Studies on this page: {len(studies_response.data)}")

           if studies_response.data:
               print("\nFirst few studies:")
               for study in studies_response.data:
                   # Access attributes of the Study model
                   print(f"- {study.study_name} (Key: {study.study_key}, Status: {study.status})")
           else:
               print("No studies found.")

   except ImednetException as e:
       print(f"API Error: {e.status_code} - {e.detail}")
   except Exception as e:
       print(f"An unexpected error occurred: {e}")

**Response Structure**

The ``list_*`` methods return a Pydantic model specific to the resource list (e.g., :class:`~imednet_sdk.models.study.StudyListResponse`). This model typically contains:

* ``data``: A list of Pydantic models representing the individual resources (e.g., a list of :class:`~imednet_sdk.models.study.Study` objects).
* ``metadata``: A :class:`~imednet_sdk.models._common.ResponseMetadata` object containing pagination information (``page``, ``size``, ``total_count``, ``total_pages``).

Getting a Specific Resource
---------------------------

To retrieve a single resource by its identifier (often a ``key`` or ``id``), use the corresponding ``get_*`` method.

**Example: Getting a Specific Site**

.. code-block:: python

   # Assuming 'client' is an initialized ImednetClient
   # and 'study_key' and 'site_key' are known

   study_key_to_get = "STUDY123"
   site_key_to_get = "SITE001"

   try:
       site = client.sites.get_site(study_key=study_key_to_get, site_key=site_key_to_get)

       print(f"Successfully retrieved site:")
       print(f"- Name: {site.site_name}")
       print(f"- Key: {site.site_key}")
       print(f"- Status: {site.status}")
       # ... access other site attributes ...

   except ImednetException as e:
       if e.status_code == 404:
           print(f"Site {site_key_to_get} not found in study {study_key_to_get}.")
       else:
           print(f"API Error: {e.status_code} - {e.detail}")
   except Exception as e:
       print(f"An unexpected error occurred: {e}")

**Response Structure**

The ``get_*`` methods typically return a single Pydantic model representing the requested resource (e.g., :class:`~imednet_sdk.models.site.Site`). If the resource is not found, an :class:`~imednet_sdk.exceptions.ImednetException` with a 404 status code is usually raised.
