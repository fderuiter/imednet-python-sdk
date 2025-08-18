Async Quick Start Script
========================

Prerequisites
-------------

* ``imednet`` package installed
* Access to an iMednet environment

Environment variables
---------------------

.. code-block:: bash

   export IMEDNET_API_KEY
   export IMEDNET_SECURITY_KEY
   export IMEDNET_BASE_URL (optional)
   export IMEDNET_JOB_STUDY_KEY (optional)
   export IMEDNET_BATCH_ID (optional)

Description
-----------

Async example listing studies and optionally polling a job.

.. literalinclude:: ../../examples/async_quick_start.py
   :language: python
