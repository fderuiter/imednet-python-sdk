Workflow Interactions
=====================

The helpers in :mod:`imednet_workflows` combine multiple endpoint calls to
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
       D -- Yes --> E[JobPoller.run]
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

Query Management
----------------

.. mermaid::

   graph TD
       A[get_open_queries] --> B[queries.list]
       B --> C{Iterate Queries}
       C --> D{Check latest comment}
       D -- closed=False --> E[Add to Open list]
       D -- closed=True --> F[Skip]
       E --> G[Return open queries]

Background Sync Worker
----------------------

:class:`~imednet_workflows.sync_worker.SyncWorker` runs incremental record
synchronisation in a background thread so that the main application thread
(e.g. a Streamlit rendering loop) never blocks on API calls.

.. mermaid::

   graph TD
       A[run_forever] --> B{stop_event set?}
       B -- No --> C[acquire FileLock]
       C --> D[load_records / delta sync]
       D --> E[reconcile hard-deletes]
       E --> F[release FileLock]
       F --> G[wait interval_seconds]
       G --> B
       B -- Yes --> H[log stopped]

**Concurrency model**

SQLite is opened in WAL mode (``PRAGMA journal_mode=WAL``) so multiple reader
connections can query the cache while a single writer holds the write-lock.
A :class:`filelock.FileLock` placed next to the database file serialises
concurrent *writers* without blocking readers at all.

Usage example
~~~~~~~~~~~~~

.. code-block:: python

   from imednet.sdk import ImednetSDK
   from imednet_workflows.cached_loader import CachedRecordsLoader
   from imednet_workflows.sync_worker import SyncWorker, SyncWorkerConfig
   import threading

   sdk = ImednetSDK(api_key="...", security_key="...")
   loader = CachedRecordsLoader(sdk)
   worker = SyncWorker(
       loader,
       config=SyncWorkerConfig(study_key="PROT-01", interval_seconds=900),
   )

   # Start the worker in a daemon thread so it stops when the main process exits.
   t = threading.Thread(target=worker.run_forever, daemon=True)
   t.start()

   # Your application reads from the cache without waiting for the API.
   records = loader.get_cached_records("PROT-01")

   worker.stop()
   t.join()
