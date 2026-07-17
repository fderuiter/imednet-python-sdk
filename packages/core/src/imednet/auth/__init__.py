"""Authentication helpers."""

from .api_key import ApiKeyAuth
from .oidc import OIDCAuth
from .strategy import AuthStrategy

__all__ = ["ApiKeyAuth", "AuthStrategy", "OIDCAuth"]

AuthStrategy.__module__ = "imednet.auth"
ApiKeyAuth.__module__ = "imednet.auth"
OIDCAuth.__module__ = "imednet.auth"
