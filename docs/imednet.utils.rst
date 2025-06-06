imednet.utils package
=====================

Submodules
----------

imednet.utils.dates module
--------------------------

.. automodule:: imednet.utils.dates
   :members:
   :undoc-members:
   :show-inheritance:

imednet.utils.filters module
----------------------------

.. automodule:: imednet.utils.filters
   :members:
   :undoc-members:
   :show-inheritance:

Building complex filter strings
-------------------------------

``build_filter_string`` accepts nested dictionaries using ``"and"`` and
``"or"`` keys to construct grouped expressions.

.. code-block:: python

   from imednet.utils import build_filter_string

   filters = {
       "and": [
           {"status": "Active"},
           {"or": [
               {"age": (">", 65)},
               {"type": ["AE", "CM"]},
           ]},
       ]
   }

   query = build_filter_string(filters)
   # 'status==Active;(age>65,type==AE,type==CM)'

For record data filtering the same helper can be used with ``;`` and ``,``
connectors:

.. code-block:: python

   record_filters = {"AESER": "Serious", "GENDER": "Male"}
   build_filter_string(record_filters, and_connector=";")
   # 'AESER==Serious;GENDER==Male'

imednet.utils.typing module
---------------------------

.. automodule:: imednet.utils.typing
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: imednet.utils
   :members:
   :undoc-members:
   :show-inheritance:
