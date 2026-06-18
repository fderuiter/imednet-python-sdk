Command Line Interface (CLI)
============================

The package installs an ``imednet`` command that wraps common SDK features. The CLI
reads authentication details from environment variables. See :doc:`configuration`
for the full list and details on using an ``.env`` file.

.. click:: imednet.cli:click_app
   :prog: imednet
   :nested: full
