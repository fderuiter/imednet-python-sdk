Command Line Interface (CLI)
============================

The package installs an ``imednet`` command that wraps common SDK features. The CLI
reads authentication details from environment variables:

``IMEDNET_API_KEY``
    Your API key.
``IMEDNET_SECURITY_KEY``
    Your security key.
``IMEDNET_BASE_URL``
    Optional base URL if not using the default cloud service.

Set these variables in your shell before invoking the command. You may also create
an ``.env`` file so the values are loaded automatically.
The CLI calls :func:`imednet.config.load_config` under the hood to read them.

Command Hierarchy
-----------------

.. mermaid::

   graph TD
       A[imednet] --> B(studies)
       A --> C(sites)
       A --> D(subjects)
       A --> E(records)
       A --> F(export)
       F --> F1(parquet)
       F --> F2(csv)
       F --> F3(excel)
       F --> F4(json)
       A --> G(jobs)
       A --> H(queries)
       A --> I(variables)
       A --> J("record-revisions")
       A --> K(workflows)
       K --> K1("extract-records")
       A --> L("subject-data")

Available Commands
------------------

.. code-block:: console

   imednet studies list
   imednet sites list <STUDY_KEY>
   imednet subjects list <STUDY_KEY> [--filter key=value ...]
   imednet records list <STUDY_KEY> [--output csv|json]
   imednet workflows extract-records <STUDY_KEY> [options]

Examples
--------

List subjects that are screened for a study and save their records as CSV:

.. code-block:: console

   imednet subjects list MY_STUDY --filter "subject_status=Screened"
   imednet records list MY_STUDY --output csv

Use ``--help`` on any command to see all options.

SQLite Exports
--------------

SQLite only allows ``2000`` columns per table. When the connection string
targets SQLite, ``export sql`` therefore creates a table for **each form** by
default:

.. code-block:: console

   imednet export sql MY_STUDY sqlite:///data.db

Use ``--single-table`` to combine everything into one table instead:

.. code-block:: console

   imednet export sql MY_STUDY table sqlite:///data.db --single-table

The constant ``imednet.integrations.export.MAX_SQLITE_COLUMNS`` still enforces
the maximum columns for any individual table.

Long-format export
------------------

Use ``--long-format`` to normalize the records into a single table with one
row per variable value. This option overrides ``--single-table`` and may
require more time to insert large datasets.

.. code-block:: console

   imednet export sql MY_STUDY table sqlite:///data.db --long-format

Variable Filters
----------------

Use ``--vars`` and ``--forms`` with ``export sql`` to limit the columns fetched
from iMednet. Both options accept comma-separated values.

.. code-block:: console

   imednet export sql MY_STUDY table sqlite:///test.db --vars AGE,SEX --forms 10,20
