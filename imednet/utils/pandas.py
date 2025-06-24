"""Pandas helpers for working with iMednet models."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

import pandas as pd

from ..models.records import Record

if TYPE_CHECKING:  # pragma: no cover - only for type checking
    from ..sdk import ImednetSDK


def records_to_dataframe(records: List[Record], *, flatten: bool = False) -> pd.DataFrame:
    """Convert a list of :class:`~imednet.models.records.Record` to a DataFrame.

    Each record is converted using :meth:`pydantic.BaseModel.model_dump` with
    ``by_alias=False``. If ``flatten`` is ``True`` the ``record_data`` column is
    expanded using :func:`pandas.json_normalize` so that each variable becomes a
    column in the resulting DataFrame.
    """

    rows = [r.model_dump(by_alias=False) for r in records]
    df = pd.DataFrame(rows)
    if flatten and not df.empty:
        record_df = pd.json_normalize(df["record_data"], sep="_")  # type: ignore[arg-type]
        df = pd.concat([df.drop(columns=["record_data"]), record_df], axis=1)
    return df


def export_records_csv(
    sdk: "ImednetSDK", study_key: str, file_path: str, *, flatten: bool = True
) -> None:
    """Fetch all records for ``study_key`` and write them to ``file_path``.

    Parameters are passed to :func:`records_to_dataframe` and the resulting
    DataFrame is written with :meth:`pandas.DataFrame.to_csv` using
    ``index=False``.
    """

    records = sdk.records.list(study_key=study_key)
    df = records_to_dataframe(records, flatten=flatten)
    df.to_csv(file_path, index=False)
