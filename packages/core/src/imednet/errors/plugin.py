"""Plugin-related errors."""

from .base import ImednetError


class PluginLoadError(ImednetError):
    """Raised when a plugin fails to load or does not satisfy the :class:`~imednet.plugins.PluginProtocol`."""
