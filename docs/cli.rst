Command Line Interface (CLI)
===========================

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
