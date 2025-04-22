.. _usage-core-concepts:

Core API Concepts
=================

Understanding a few core concepts of the iMednet API will help you use this SDK more effectively.

Resource Hierarchy
------------------

Many iMednet resources exist within a hierarchy:

*   **Study:** The top-level container for clinical trial data (e.g., `STUDY123`).
*   **Site:** A physical location participating in a study (e.g., `SITE001`). A study can have multiple sites.
*   **Subject:** A participant enrolled in a study, usually at a specific site (e.g., `SUBJ001`).

When accessing resources like sites, subjects, or records, you often need to provide the `study_key`.

Data Collection Structure
-------------------------

Clinical data is typically organized using these components:

*   **Form:** A template defining a set of data points to be collected (e.g., `FORM_DEMOG`, `FORM_VITALS`). Forms contain Variables.
*   **Variable:** A specific data field within a form (e.g., `VAR_AGE`, `VAR_HR`).
*   **Visit:** A scheduled or unscheduled event during which data is collected (e.g., `VISIT_BASELINE`, `VISIT_WEEK4`).
*   **Record:** An instance of data collected for a specific Subject, using a specific Form, often during a specific Visit. Records contain the actual values entered for the variables.

Keys as Identifiers
-------------------

Most resources in iMednet are identified by unique keys:

*   `study_key`
*   `site_key`
*   `subject_key`
*   `form_key`
*   `visit_key`
*   `record_key`
*   `variable_key`

These keys are crucial when making API calls to retrieve, create, or update specific resources.

Asynchronous Operations (Jobs)
------------------------------

Operations that might take a significant amount of time, such as bulk record creation or complex data exports, are often handled asynchronously by the iMednet API.

1.  You make an initial API request (e.g., using `client.records.create_records`).
2.  The API validates the request and, if valid, starts a background **Job**.
3.  The immediate API response contains information about the job, typically including a `job_id`.
4.  You need to use a separate endpoint (e.g., `client.jobs.get_job_status(job_id=...)`) to poll the status of the job until it completes (successfully or with errors).

Standard Response Structure
---------------------------

Many SDK methods that retrieve data return Pydantic models that follow a common structure:

*   **List Responses:** Contain a `data` attribute (a list of resource models) and a `metadata` attribute (containing pagination info like `total_count`, `page`, `size`, `total_pages`). See :class:`~imednet_sdk.models._common.ResponseMetadata`.
*   **Single Resource Responses:** Directly return the Pydantic model for the requested resource (e.g., :class:`~imednet_sdk.models.study.Study`, :class:`~imednet_sdk.models.site.Site`).
