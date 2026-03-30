import pytest


def test_async_sdk_deprecation_warning():
    import sys

    if "imednet.async_sdk" in sys.modules:
        del sys.modules["imednet.async_sdk"]

    with pytest.warns(
        DeprecationWarning, match="imednet.async_sdk is deprecated; use imednet.sdk instead"
    ):
        import imednet.async_sdk

        assert hasattr(imednet.async_sdk, "AsyncImednetSDK")
