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

Understanding ``DatasetMetadata``
---------------------------------

The ``column_prefix_map`` passed to
``DatasetVariable`` typically references the dataset domain derived from
``SDTMDatasetMetadata``.  This metadata class exposes convenient properties for
determining the domain name and whether a supplemental qualifier dataset is
split.  The CDISC rules engine uses this information to map shorthand variable
names (such as ``--SEQ``) to their fully qualified column names.

.. code-block:: python

   from dataclasses import dataclass
   from typing import Union
   from cdisc_rules_engine.models.dataset_metadata import DatasetMetadata
   from cdisc_rules_engine.constants.domains import SUPPLEMENTARY_DOMAINS

   @dataclass
   class SDTMDatasetMetadata(DatasetMetadata):
       """Container for SDTM dataset metadata."""

       @property
       def domain(self) -> Union[str, None]:
           return (self.first_record or {}).get("DOMAIN", None)

       @property
       def rdomain(self) -> Union[str, None]:
           return (self.first_record or {}).get("RDOMAIN", None) if self.is_supp else None

       @property
       def is_supp(self) -> bool:
           return self.name.startswith(SUPPLEMENTARY_DOMAINS)

       @property
       def unsplit_name(self) -> str:
           if self.domain:
               return self.domain
           if self.name.startswith("SUPP"):
               return f"SUPP{self.rdomain}"
           if self.name.startswith("SQ"):
               return f"SQ{self.rdomain}"
           return self.name

       @property
       def is_split(self) -> bool:
           return self.name != self.unsplit_name

With this metadata in hand you can construct ``DatasetVariable`` objects like
so::

   dataset_variable = DatasetVariable(
       dataset,
       column_prefix_map={"--": dataset_metadata.domain},
   )

This dynamic mapping ensures variables are interpreted correctly based on their
domain context.
