Record Mapping Process
======================

:class:`~imednet_workflows.record_mapper.RecordMapper` turns raw record payloads
into a :class:`pandas.DataFrame`. It loads variable metadata, builds a dynamic
model, parses the records, and assembles the final table.

.. mermaid:: /diagrams/record_mapping_13.mmd