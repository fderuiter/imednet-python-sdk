import pandas as pd
from imednet.utils.typing import DataFrame


def test_dataframe_alias() -> None:
    assert DataFrame is pd.DataFrame
