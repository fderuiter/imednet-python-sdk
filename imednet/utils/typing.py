"""
Type definitions for imednet SDK utilities.
"""

from typing import TYPE_CHECKING, Any, Dict

try:
    import pandas as pd
    DataFrame = pd.DataFrame
except ImportError:
    DataFrame = Any  # type: ignore

if TYPE_CHECKING:
    try:
        from pandas import DataFrame as PandasDataFrame
        DataFrame = PandasDataFrame # type: ignore
    except ImportError:
        pass

JsonDict = Dict[str, Any]
