Export Long SQL Script
======================

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

Description
-----------

Export study records to a long-format SQL table.

.. literalinclude:: ../../examples/export_long_sql.py
   :language: python
