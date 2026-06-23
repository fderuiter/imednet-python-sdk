"""TODO: Add docstring."""

import importlib
import warnings

warnings.warn(
    "imednet.async_sdk is deprecated; use imednet.sdk instead "
    "(deprecated in 0.6.0, to be removed in 0.8.0)",
    DeprecationWarning,
    stacklevel=2,
)
AsyncImednetSDK = importlib.import_module("imednet.sdk").AsyncImednetSDK
