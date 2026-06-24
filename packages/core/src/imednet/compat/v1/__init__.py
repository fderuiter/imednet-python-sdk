"""Legacy v1 compatibility namespace."""

import logging
import warnings

from .facades import execute_list_async, execute_list_sync, is_async_client
from .identifiers import ItemId
from .operations import get_resource_async, get_resource_sync

logger = logging.getLogger(__name__)

msg = "Plugin initialized using legacy compatibility namespace (compat.v1). Please migrate to the modern core APIs."
warnings.warn(msg, DeprecationWarning, stacklevel=2)
logger.warning(msg)

__all__ = [
    "execute_list_sync",
    "execute_list_async",
    "is_async_client",
    "get_resource_sync",
    "get_resource_async",
    "ItemId",
]
