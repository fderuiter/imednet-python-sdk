"""TODO: Add docstring."""

import pytest


def test_async_sdk_deprecation_warning():
    """TODO: Add docstring."""
    import sys

    if "imednet.async_sdk" in sys.modules:
        del sys.modules["imednet.async_sdk"]

    with pytest.warns(
        DeprecationWarning, match=r"imednet\.async_sdk is deprecated; use imednet\.sdk instead \(deprecated in 0\.6\.0, to be removed in 0\.8\.0\)"
    ):
        import imednet.async_sdk

        assert hasattr(imednet.async_sdk, "AsyncImednetSDK")
