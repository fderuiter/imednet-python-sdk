Tutorials
=========

This section walks through common tasks using the ``imednet-python-sdk``. Each
tutorial assumes that you have installed the package and configured your API
credentials as environment variables as shown in the :doc:`README <../README>`.

Authenticating and fetching studies
-----------------------------------

The quickest way to start using the SDK is to create an ``ImednetSDK`` instance
and list the studies you have access to.

.. code-block:: python

   from imednet.sdk import ImednetSDK

   sdk = ImednetSDK(api_key="<API_KEY>", security_key="<SECURITY_KEY>")
   studies = sdk.studies.list()
   for study in studies:
       print(study.study_name, study.study_key)

Registering subjects
--------------------

The :class:`~imednet.workflows.register_subjects.RegisterSubjectsWorkflow`
workflow provides a convenient way to register multiple subjects in a study.

.. code-block:: python

   import json
   from imednet.sdk import ImednetSDK
   from imednet.workflows.register_subjects import RegisterSubjectsWorkflow

   sdk = ImednetSDK(api_key="<API_KEY>", security_key="<SECURITY_KEY>")
   workflow = RegisterSubjectsWorkflow(sdk)

   with open("subjects.json", "r", encoding="utf-8") as f:
       subjects = json.load(f)

   result = workflow.register_subjects(study_key="MY_STUDY", subjects=subjects)
   print(result)

Managing queries
----------------

Queries can be inspected using the
:class:`~imednet.workflows.query_management.QueryManagementWorkflow`.
The following example retrieves all open queries for a study.

.. code-block:: python

   from imednet.sdk import ImednetSDK
   from imednet.workflows.query_management import QueryManagementWorkflow

   sdk = ImednetSDK(api_key="<API_KEY>", security_key="<SECURITY_KEY>")
   qm = QueryManagementWorkflow(sdk)

   open_queries = qm.get_open_queries("MY_STUDY")
   for query in open_queries:
       print(query.query_id, query.record_id)
