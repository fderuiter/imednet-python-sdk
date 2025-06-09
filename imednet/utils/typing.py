"""
Type definitions for imednet SDK utilities.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from pandas import DataFrame
else:  # pragma: no cover - pandas is optional
    DataFrame = Any

JsonDict = Dict[str, Any]

__all__ = ["JsonDict", "DataFrame"]
