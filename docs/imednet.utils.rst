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

imednet.utils.pandas module
---------------------------
.. automodule:: imednet.utils.pandas
   :members:
   :undoc-members:
   :show-inheritance:

imednet.utils.typing module
---------------------------

.. automodule:: imednet.utils.typing
   :members:
   :undoc-members:
   :show-inheritance:

imednet.utils.json_logging module
---------------------------------

.. automodule:: imednet.utils.json_logging
   :members:
   :undoc-members:
   :show-inheritance:

Example
-------

.. code-block:: python

   >>> from imednet.utils.json_logging import configure_json_logging
   >>> configure_json_logging()
   >>> import logging
   >>> logging.getLogger(__name__).warning("hi")  # doctest: +ELLIPSIS
   {"message": "hi", "level": "warning", ...}

imednet.utils.url module
------------------------

.. automodule:: imednet.utils.url
   :members:
   :undoc-members:
   :show-inheritance:

Example
-------

.. code-block:: python

   >>> from imednet.utils.url import sanitize_base_url
   >>> sanitize_base_url("https://example.com/api/")
   'https://example.com'

imednet.utils.validators module
-------------------------------

.. automodule:: imednet.utils.validators
   :members:
   :undoc-members:
   :show-inheritance:

Examples
--------

.. code-block:: python

   >>> from imednet.utils.validators import (
   ...     parse_bool,
   ...     parse_datetime,
   ...     parse_int_or_default,
   ...     parse_str_or_default,
   ...     parse_list_or_default,
   ...     parse_dict_or_default,
   ... )
   >>> parse_bool("true")
   True
   >>> parse_datetime("2020-01-02T03:04:05Z").year
   2020
   >>> parse_int_or_default("bad", default=2)
   2
   >>> parse_str_or_default(123)
   '123'
   >>> parse_list_or_default("a")
   ['a']
   >>> parse_dict_or_default(None)
   {}

Module contents
---------------

.. automodule:: imednet.utils
   :members:
   :undoc-members:
   :exclude-members: DataFrame
   :show-inheritance:
