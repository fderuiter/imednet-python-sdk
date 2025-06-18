CDISC Validation
================

This section describes how to validate SDTM datasets using the CDISC rules
engine. Two approaches are provided:

Step 0: Install the Library
---------------------------
Install the ``cdisc-rules-engine`` package and download the bundled rule cache.

.. code-block:: bash

   pip install cdisc-rules-engine

Step 1: Load the Rules
----------------------
Load the pickled rule files into an in-memory cache and retrieve the rules for
your standard and version.

.. code-block:: python

   from imednet.validation import load_rules_cache, get_rules

   cache = load_rules_cache("path/to/rules/cache")
   rules = get_rules(cache, "sdtmig", "3-4")

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

Complete End-to-End Example
---------------------------

The following script demonstrates loading a rules cache, reading an XPT file and
validating AE domain rules using the low level business rules engine.

.. code-block:: python

   import os
   import pathlib
   import pickle
   import pandas as pd
   import pyreadstat
   from multiprocessing import freeze_support
   from multiprocessing.managers import SyncManager
   from cdisc_rules_engine.services.cache import InMemoryCacheService
   from cdisc_rules_engine.utilities.utils import get_rules_cache_key
   from cdisc_rules_engine.models.dataset.pandas_dataset import PandasDataset
   from cdisc_rules_engine.models.dataset_variable import DatasetVariable
   from cdisc_rules_engine.models.sdtm_dataset_metadata import SDTMDatasetMetadata
   from cdisc_rules_engine.models.actions import COREActions
   from business_rules.engine import run

   class CacheManager(SyncManager):
       pass

   CacheManager.register("InMemoryCacheService", InMemoryCacheService)

   def load_rules_cache(path_to_rules_cache):
       cache_path = pathlib.Path(path_to_rules_cache)
       manager = CacheManager()
       manager.start()
       cache = manager.InMemoryCacheService()
       files = next(os.walk(cache_path), (None, None, []))[2]
       for fname in files:
           with open(cache_path / fname, "rb") as f:
               cache.add_all(pickle.load(f))
       return cache

   def main():
       current_dir = os.getcwd()
       cache_path = os.path.join(current_dir, "cache")
       ae_file_path = os.path.join(current_dir, "ae.xpt")

       cache = load_rules_cache(cache_path)
       cache_key_prefix = get_rules_cache_key("sdtmig", "3-4")
       rules = cache.get_all_by_prefix(cache_key_prefix)

       ae_data, meta = pyreadstat.read_xport(ae_file_path)
       pandas_dataset = PandasDataset(data=ae_data)
       dataset_metadata = SDTMDatasetMetadata(
           name="AE",
           label=meta.file_label if hasattr(meta, "file_label") else "Adverse Events",
           first_record=ae_data.iloc[0].to_dict() if not ae_data.empty else None,
       )
       dataset_variable = DatasetVariable(
           pandas_dataset,
           column_prefix_map={"--": dataset_metadata.domain},
       )

       ae_rules = [
           rule for rule in rules
           if "AE" in rule.get("domains", {}).get("Include", []) or
              "ALL" in rule.get("domains", {}).get("Include", [])
       ]

       all_results = []
       for rule in ae_rules:
           results = []
           core_actions = COREActions(
               output_container=results,
               variable=dataset_variable,
               dataset_metadata=dataset_metadata,
               rule=rule,
               value_level_metadata=None,
           )
           triggered = run(
               rule=rule,
               defined_variables=dataset_variable,
               defined_actions=core_actions,
           )
           if triggered and results:
               all_results.extend(results)

       print("\n===== VALIDATION SUMMARY =====")
       print(f"Total rules checked: {len(ae_rules)}")
       print(f"Total issues found: {len(all_results)}")

    if __name__ == "__main__":
        freeze_support()
        main()

Option B Walkthrough
-------------------
The higher level ``RulesEngine`` API automates dataset loading and rule
evaluation.

Step 2: Prepare Your Data
^^^^^^^^^^^^^^^^^^^^^^^^^
Create :class:`~cdisc_rules_engine.models.sdtm_dataset_metadata.SDTMDatasetMetadata`
objects for your XPT files.

.. code-block:: python

   from imednet.validation import create_dataset_metadata, get_datasets_metadata

   datasets = get_datasets_metadata("path/to/datasets")

Step 3: Initialize Library Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Build a library metadata container using the loaded cache.

.. code-block:: python

   library_metadata = build_library_metadata(
       cache,
       standard="sdtmig",
       standard_version="3-4",
       ct_packages=["sdtmct-2021-12-17"],
   )

Step 4: Initialize Data Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create a data service for the dataset paths.

.. code-block:: python

   paths = [d.full_path for d in datasets]
   max_size = max(d.file_size for d in datasets)
   data_service = get_data_service(
       paths,
       cache,
       standard="sdtmig",
       standard_version="3-4",
       standard_substandard=None,
       library_metadata=library_metadata,
       max_dataset_size=max_size,
   )

Step 5: Initialize Rules Engine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Instantiate the ``RulesEngine`` for validation.

.. code-block:: python

   rules_engine = create_rules_engine(
       cache=cache,
       data_service=data_service,
       library_metadata=library_metadata,
       standard="sdtmig",
       standard_version="3-4",
       dataset_paths=paths,
       ct_packages=["sdtmct-2021-12-17"],
   )

Step 6: Run Validation
^^^^^^^^^^^^^^^^^^^^^^
Evaluate rules against the datasets.

.. code-block:: python

   results = validate_rules(rules_engine, rules, datasets)

Step 7: Generate Report
^^^^^^^^^^^^^^^^^^^^^^^
Write the results to a file.

.. code-block:: python

   from imednet.validation import write_validation_report

   write_validation_report(results, "validation_results.txt")

Troubleshooting
---------------
Check the following if you encounter errors:

- All required columns exist in your dataframe and match the rule domains.
- ``column_prefix_map`` correctly maps variable prefixes to domains.
- Controlled terminology for each variable is available in ``column_codelist_map``.
- ``DatasetVariable`` objects include all required metadata and use ``PandasDataset``.
- ``SDTMDatasetMetadata`` has a valid ``domain`` and ``full_path`` when using
  the ``RulesEngine`` approach.
- The rules' domain inclusion criteria match the dataset domain.
- The cache contains controlled terminology packages used for validation.
- ``standard_version`` uses dashes instead of periods.
- File paths for external dictionaries and ``define.xml`` are accessible.
