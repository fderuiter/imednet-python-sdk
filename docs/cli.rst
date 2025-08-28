Command Line Interface (CLI)
============================

The package installs an ``imednet`` command that wraps common SDK features. The CLI
reads authentication details from environment variables. See :doc:`configuration`
for the full list and details on using an ``.env`` file. The CLI calls
:func:`imednet.config.load_config_from_env` under the hood to read these values.

Command Hierarchy

Global Options
--------------

The CLI supports several global flags and behaviors:

- ``--help``: Show help for any command or subcommand.
- ``--version``: Print the CLI version and exit.
- ``.env`` loading: If a ``.env`` file is present in the working directory, environment variables are loaded automatically.

Example:

.. code-block:: console

   $ imednet --version
   imednet, version X.Y.Z
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
   imednet variables list <STUDY_KEY>
   imednet queries list <STUDY_KEY>
   imednet record-revisions list <STUDY_KEY>
   imednet jobs status <STUDY_KEY> <BATCH_ID>
   imednet jobs wait <STUDY_KEY> <BATCH_ID> [--interval N] [--timeout N]
   imednet subject-data <STUDY_KEY> <SUBJECT_KEY>
   imednet export sql <STUDY_KEY> table sqlite:///data.db [options]
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

See the example script :doc:`examples/export_long_sql` for invoking this option
via the SDK.

Variable Filters
----------------

Use ``--vars`` and ``--forms`` with ``export sql`` to limit the columns fetched
from iMednet. Both options accept comma-separated values.

.. code-block:: console

   imednet export sql MY_STUDY table sqlite:///test.db --vars AGE,SEX --forms 10,20

Jobs
----

Use ``jobs`` to monitor background tasks created by the API. ``jobs status`` fetches the
current state of a job batch, while ``jobs wait`` polls until the job reaches a terminal
state.

.. code-block:: console

   imednet jobs status MY_STUDY 12345
   imednet jobs wait MY_STUDY 12345 --interval 10 --timeout 600

``status`` prints the job's JSON payload. ``wait`` repeats the check every ``--interval``
seconds until completion or until ``--timeout`` is reached. A typical workflow is to
start an export job and then wait for completion before downloading results.

Queries
-------

``queries list`` shows all queries for a study.

.. code-block:: console

   imednet queries list MY_STUDY

Each query is printed as JSON, allowing teams to review outstanding data issues.

Variables
---------

``variables list`` returns the variable definitions for a study.

.. code-block:: console

   imednet variables list MY_STUDY

The output includes keys, labels, and data types, which is useful when constructing
record payloads.

Record Revisions
----------------

``record-revisions list`` displays the revision history for a study's records.

.. code-block:: console

   imednet record-revisions list MY_STUDY

Entries show the record key, revision number, and timestamp so you can audit changes
over time.

Subject Data
------------

``subject-data`` retrieves all forms and variables for a single subject.

.. code-block:: console

   imednet subject-data MY_STUDY SUBJ001

The command prints a nested JSON structure containing the subject's visits, forms, and
variable values. This is helpful for debugging or exporting an individual subject's
dataset.
