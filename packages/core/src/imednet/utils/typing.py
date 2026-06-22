"""Type definitions for imednet SDK utilities."""

from typing import Any, Dict, List, Tuple, Union

try:
    from pandas import DataFrame
except ImportError:
    DataFrame = Any  # type: ignore

#: Generic JSON object type (mapping of string keys to arbitrary values).
JsonDict = Dict[str, Any]

#: Accepted types for an endpoint item-ID parameter (path segment or filter value).
ItemId = Union[str, int]

#: A single filter value accepted by endpoint ``list`` and convenience methods.
#:
#: Supported forms:
#:
#: * A scalar ``str``, ``int``, ``float``, or ``bool`` – implies equality.
#: * A two-element tuple ``(operator, scalar)`` – e.g. ``(">", 30)``.
#: * A :class:`list` of scalars – generates ``OR``-joined equality filters.
FilterScalar = Union[str, int, float, bool, None]
FilterValue = Union[FilterScalar, Tuple[str, FilterScalar], List[FilterScalar]]

__all__ = ["JsonDict", "ItemId", "FilterValue", "FilterScalar", "DataFrame"]
