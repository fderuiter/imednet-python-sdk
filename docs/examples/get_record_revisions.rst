List Record Revisions
=====================

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

Fetch record revisions for a study.

.. literalinclude:: ../../examples/basic/get_record_revisions.py
   :language: python
