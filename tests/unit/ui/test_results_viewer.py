import json
import time
from pathlib import Path

import pandas as pd
from imednet.ui.results_viewer import ResultsViewer


def test_to_dataframe_large() -> None:
    data = [{"a": i} for i in range(10000)]
    start = time.perf_counter()
    df = ResultsViewer.to_dataframe(data)
    duration = time.perf_counter() - start
    assert len(df) == 10000
    assert duration < 1


def test_to_json_dataframe() -> None:
    df = pd.DataFrame({"a": [1, 2]})
    result = ResultsViewer.to_json(df)
    assert result == [{"a": 1}, {"a": 2}]


def test_export_helpers(tmp_path: Path) -> None:
    df = pd.DataFrame({"a": [1]})
    csv_path = tmp_path / "out.csv"
    ResultsViewer.export_csv(df, csv_path)
    assert csv_path.exists()

    data = [{"a": 1}]
    json_path = tmp_path / "out.json"
    ResultsViewer.export_json(data, json_path)
    loaded = json.loads(json_path.read_text())
    assert loaded == data
