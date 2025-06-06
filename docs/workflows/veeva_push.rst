Veeva Push Workflow
===================

The :class:`~imednet.workflows.veeva_push.VeevaPushWorkflow` provides a
straightforward way to validate and send iMednet record data to Veeva Vault.

Example usage::

   from imednet.veeva import VeevaVaultClient
   from imednet.workflows.veeva_push import VeevaPushWorkflow

   client = VeevaVaultClient(
       vault="myvault",
       client_id="<id>",
       client_secret="<secret>",
       username="user",
       password="pass",
   )
   client.authenticate()

   workflow = VeevaPushWorkflow(client)
   record = {"name__v": "Sample", "status__v": "New"}
   workflow.push_record("prod__c", record)

The workflow uses
:func:`~imednet.veeva.validate_record_for_upsert` to ensure that records
contain required fields and valid picklist values before calling
:meth:`~imednet.veeva.VeevaVaultClient.upsert_object`.

