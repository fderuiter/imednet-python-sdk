"""
Type definitions for imednet SDK utilities.
"""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from pandas import DataFrame as PandasDataFrame
else:
    PandasDataFrame = Any

try:  # pragma: no cover - optional dependency
    import pandas as pd

    DataFrame = pd.DataFrame
except Exception:
    DataFrame = PandasDataFrame

JsonDict = Dict[str, Any]
