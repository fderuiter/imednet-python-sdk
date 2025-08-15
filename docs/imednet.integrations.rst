imednet.integrations package
============================

Long-format SQL export
----------------------

The :func:`imednet.integrations.export.export_to_long_sql` helper writes all
record values into a single normalized SQL table. Each row contains a record
identifier, form identifier, variable name, value, and timestamp.

Parameters:

``sdk``
    An initialized :class:`imednet.ImednetSDK` or compatible client.
``study_key``
    The study identifier.
``table_name``
    Target table for inserted rows.
``conn_str``
    SQLAlchemy connection string, such as ``sqlite:///records.db``.
``chunk_size``
    Optional batch size for insert operations (default ``1000``).

.. code-block:: python

    from imednet import ImednetSDK
    from imednet.integrations import export_to_long_sql

    sdk = ImednetSDK()
    export_to_long_sql(sdk, "STUDY", "records", "sqlite:///records.db")

The example script :mod:`examples.export_long_sql` provides a runnable
demonstration.

Subpackages
-----------

.. toctree::
   :maxdepth: 4

   imednet.integrations.airflow

Submodules
----------

imednet.integrations.export module
----------------------------------

.. automodule:: imednet.integrations.export
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: imednet.integrations
   :members:
   :undoc-members:
   :show-inheritance:
