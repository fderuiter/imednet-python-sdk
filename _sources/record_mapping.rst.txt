Record Mapping Process
======================

:class:`~imednet.workflows.record_mapper.RecordMapper` turns raw record payloads
into a :class:`pandas.DataFrame`. It loads variable metadata, builds a dynamic
model, parses the records, and assembles the final table.

.. mermaid::

   graph TD
       A[dataframe()] --> B[_fetch_variable_metadata]
       B --> C[variables.list]
       C --> D[variable keys / labels]
       A --> E[_build_record_model]
       E --> F[dynamic BaseModel]
       A --> G[_fetch_records]
       G --> H[records.list]
       A --> I[_parse_records]
       I --> J[row dicts]
       A --> K[_build_dataframe]
       K --> L[DataFrame]
       L --> M[return result]
