from typing import Any, Sequence
import pandas as pd

def models_to_frame(models: Sequence[Any], *, date_column: str | None = None) -> pd.DataFrame:
    """Convert a sequence of models into a pandas DataFrame."""
    if not models:
        return pd.DataFrame()
    rows = [
        model.model_dump(mode="python", by_alias=False) if hasattr(model, "model_dump") else dict(vars(model))
        for model in models
    ]
    df = pd.DataFrame(rows)
    if date_column and date_column in df:
        df[date_column] = pd.to_datetime(df[date_column], utc=True, errors="coerce")
    return df
