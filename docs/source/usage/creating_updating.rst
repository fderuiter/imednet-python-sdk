.. _usage-creating-updating:

Creating and Updating Resources
===============================

Besides retrieving data, the SDK allows you to create new resources or update existing ones where the iMednet API supports it.

Creating Resources
------------------

Creation is typically handled by ``create_*`` methods on the relevant resource client. These methods usually require the necessary data for the new resource, often structured as a Pydantic model or a list of models.

**Example: Creating Records**

The :meth:`~imednet_sdk.api.records.RecordsClient.create_records` method allows you to create one or more new records within a study.

1.  **Prepare the Data:**
    You need to provide a list of objects containing the data for the new records. The exact structure depends on the iMednet API requirements for record creation (e.g., subject key, form key, visit key, and variable data).

    .. note::
       Currently, the SDK uses basic dictionaries or lists for the payload in `create_records` as the exact request structure for complex data like record values isn't fully modeled in Pydantic yet. This might be refined in future versions.

2.  **Call the Method:**
    Pass the study key and the list of record data to the ``create_records`` method.

.. code-block:: python

   from imednet_sdk import ImednetClient
   from imednet_sdk.exceptions import ImednetException

   study_key_to_use = "STUDY123"

   # Example data for two new records (structure may vary based on API needs)
   new_records_data = [
       {
           "subject_key": "SUBJ001",
           "form_key": "FORM_DEMOG",
           "visit_key": "VISIT_BASELINE",
           "record_data": {
               "VAR_AGE": 35,
               "VAR_SEX": "Female"
           }
       },
       {
           "subject_key": "SUBJ002",
           "form_key": "FORM_VITALS",
           "visit_key": "VISIT_WEEK4",
           "record_data": {
               "VAR_HR": 72,
               "VAR_BP_SYS": 120,
               "VAR_BP_DIA": 80
           }
       }
   ]

   try:
       with ImednetClient() as client:
           print(f"Attempting to create {len(new_records_data)} records in study '{study_key_to_use}'...")

           # The create_records method likely returns information about the background job
           job_info = client.records.create_records(
               study_key=study_key_to_use,
               records_data=new_records_data
           )

           print("Record creation request submitted successfully.")
           # The response often contains details about the background job started
           # for processing the creation request.
           print(f"Job Info: {job_info}")
           # You might need to use client.jobs.get_job_status(job_id=...) to track completion.

   except ImednetException as e:
       print(f"API Error: {e.status_code} - {e.detail}")
       # Handle specific errors, e.g., validation errors (400)
   except Exception as e:
       print(f"An unexpected error occurred: {e}")

**Response Structure**

Creation endpoints, especially for bulk operations like creating records, often initiate a background job on the iMednet server. The immediate response might not be the created resources themselves, but rather information about the job that was started (e.g., a job ID). You may need to use a separate endpoint (like ``client.jobs.get_job_status``) to check the status and outcome of the creation process.

Updating Resources (General Concept)
------------------------------------

Updating existing resources typically involves:

1.  Identifying the resource to update (e.g., by its key or ID).
2.  Providing the data fields that need to be changed.
3.  Calling an ``update_*`` method on the corresponding resource client (e.g., ``client.subjects.update_subject(...)`` - *method name is hypothetical*).

.. note::
   Specific ``update_*`` methods are not yet implemented in all resource clients in this version of the SDK. The implementation would follow a pattern similar to creation, likely accepting the resource identifier and a Pydantic model or dictionary containing the fields to update.
