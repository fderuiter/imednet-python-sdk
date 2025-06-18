CDISC Validation
================

This section describes how to validate SDTM datasets using the CDISC rules
engine. Two approaches are provided:

Option A uses the low level ``business_rules`` package to execute each rule
directly.  Option B relies on the higher level ``RulesEngine`` which performs
additional preprocessing and aggregation.

Option A: Direct Business Rules
-------------------------------

Create a :class:`~cdisc_rules_engine.models.dataset_variable.DatasetVariable`
from a ``pandas`` dataframe and run each rule with
:func:`~business_rules.engine.run`. The return value indicates whether the rule
was triggered.  Any violations are appended to the results container passed to
:class:`~cdisc_rules_engine.models.actions.COREActions`.

.. code-block:: python

   import pandas as pd
   from imednet.validation import dataset_variable_from_dataframe, run_business_rules

   df = pd.read_csv("ae.csv")
   dv, meta = dataset_variable_from_dataframe(df, "AE")
   results = run_business_rules(rules, dv, meta)
   for violation in results:
       print(violation)

A ``False`` result means no errors were found.  ``True`` indicates violations
were written to the results list. Each violation has keys such as
``domain``, ``variables`` and ``errors`` describing the issue.

Option B: Using ``RulesEngine``
-------------------------------

When physical dataset files are available you can take advantage of the
``RulesEngine`` which loads datasets, library metadata and controlled
terminology.  Build a data service and engine then call
:func:`~imednet.validation.validate_rules` to produce
:class:`~cdisc_rules_engine.models.rule_validation_result.RuleValidationResult`
objects.

Both approaches rely on the dataset abstraction layer.  For in-memory data use
:class:`~cdisc_rules_engine.models.dataset.pandas_dataset.PandasDataset`.  A
``DaskDataset`` implementation is also available for larger files.
