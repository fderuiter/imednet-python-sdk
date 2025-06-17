Workflow Interactions
=====================

The helpers in :mod:`imednet.workflows` combine multiple endpoint calls to
automate common tasks. The diagrams below outline the main steps in each workflow.

Data Extraction
---------------

.. mermaid::

   graph TD
       A[extract_records_by_criteria] --> B[subjects.list]
       A --> C[visits.list]
       A --> D[records.list]
       B --> E{subject keys}
       C --> F{visit ids}
       D --> G{apply filters}
       E --> G
       F --> G
       G --> H[return records]

Record Update
-------------

.. mermaid::

   graph TD
       A[create_or_update_records] --> B[validate_batch]
       B --> C[records.create]
       C --> D{wait?}
       D -- Yes --> E[JobPoller.wait]
       D -- No --> F[return Job]
       E --> F

Subject Data
------------

.. mermaid::

   graph TD
       A[get_all_subject_data] --> B[subjects.list]
       A --> C[visits.list]
       A --> D[records.list]
       A --> E[queries.list]
       B --> F[aggregate]
       C --> F
       D --> F
       E --> F
       F --> G[return SubjectComprehensiveData]
