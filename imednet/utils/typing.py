"""
Type definitions for imednet SDK utilities.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    try:
        from pandas import DataFrame
    except ImportError:
        DataFrame = Any  # type: ignore
else:
    DataFrame = Any

JsonDict = Dict[str, Any]
