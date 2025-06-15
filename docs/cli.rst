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

SQLite Column Limit
-------------------

The ``export sql`` command writes records to a database using
``export_to_sql``. When the destination is SQLite, tables are limited to
``2000`` columns. The helper checks this against
``imednet.integrations.export.MAX_SQLITE_COLUMNS`` and raises a friendly
error if exceeded. Use another backend if your study contains more
variables.
