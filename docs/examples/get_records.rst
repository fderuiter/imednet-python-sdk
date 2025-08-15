List Records
============

Prerequisites
-------------

* ``imednet`` package installed
* Access to an iMednet environment

Environment variables
---------------------

.. code-block:: bash

   export IMEDNET_API_KEY
   export IMEDNET_SECURITY_KEY
   export IMEDNET_STUDY_KEY
   export IMEDNET_BASE_URL (optional)

Description
-----------

Fetch records for a study.

.. literalinclude:: ../../examples/basic/get_records.py
   :language: python
