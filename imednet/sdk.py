# imednet/sdk.py
from .core.client import Client
from .core.context import Context


class ImednetSDK:
    """Public entry-point for library users."""

    def __init__(self, api_key: str, security_key: str):
        self.ctx = Context()
        self._client = Client(api_key, security_key)
        # future: wire endpoints and workflows here

    # trivial helper so object is not “empty”
    def ping(self) -> str:
        return "imednet-sdk is alive"
