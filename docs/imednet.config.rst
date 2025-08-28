imednet.config module
=====================

The :mod:`imednet.config` module provides a simple dataclass for SDK credentials
and a helper to populate it from environment variables.

Example
-------

.. code-block:: python

    import os
    from imednet.config import load_config_from_env

    os.environ["IMEDNET_API_KEY"] = "A"
    os.environ["IMEDNET_SECURITY_KEY"] = "B"

    config = load_config_from_env()
    assert config.api_key == "A"

.. automodule:: imednet.config
   :members: Config, load_config_from_env
   :undoc-members:
   :show-inheritance:
