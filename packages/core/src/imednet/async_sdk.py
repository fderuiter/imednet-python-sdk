import importlib
import warnings

warnings.warn(
    "imednet.async_sdk is deprecated; use imednet.sdk instead",
    DeprecationWarning,
    stacklevel=2,
)
AsyncImednetSDK = importlib.import_module("imednet.sdk").AsyncImednetSDK
