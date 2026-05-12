"""
Type definitions for imednet SDK utilities.
"""

from typing import Any, Dict

try:
    from pandas import DataFrame
except ImportError:
    DataFrame = Any  # type: ignore

JsonDict = Dict[str, Any]
