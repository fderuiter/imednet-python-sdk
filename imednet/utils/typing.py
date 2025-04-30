"""
Type definitions for imednet SDK utilities.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    # for static checking, get the real pandas DataFrame
    from pandas import DataFrame
else:
    # at runtime, alias DataFrame to pandas.DataFrame if available,
    # otherwise fall back to Any
    try:
        import pandas as _pd

        DataFrame = _pd.DataFrame
    except (ImportError, AttributeError):
        DataFrame = Any  # type: ignore

JsonDict = Dict[str, Any]
__all__ = ["DataFrame", "JsonDict"]
