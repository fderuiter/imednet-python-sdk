from __future__ import annotations

import pandas as pd

from imednet_streamlit.components.paginated_grid import top_n_with_other


def test_top_n_with_other_adds_remainder_bucket() -> None:
    df = pd.DataFrame(
        {
            "label": ["A", "B", "C", "D"],
            "count": [10, 8, 3, 2],
        }
    )

    result = top_n_with_other(df, label_column="label", value_column="count", top_n=2)

    assert result["label"].tolist() == ["A", "B", "Other"]
    assert result["count"].tolist() == [10, 8, 5]
