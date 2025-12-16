import pandas as pd
from unittest.mock import MagicMock
import imednet.integrations.export as export_mod

def test_export_to_csv_sanitization(tmp_path, monkeypatch):
    # Mock RecordMapper
    df = pd.DataFrame({
        "safe": ["hello"],
        "unsafe": ["=cmd"]
    })
    mapper_inst = MagicMock()
    mapper_inst.dataframe.return_value = df
    monkeypatch.setattr(export_mod, "RecordMapper", MagicMock(return_value=mapper_inst))

    sdk = MagicMock()
    path = tmp_path / "out.csv"

    export_mod.export_to_csv(sdk, "STUDY", str(path))

    # Check output
    content = path.read_text()
    # Pandas to_csv might quote fields.
    # Expected: header\nhello,'=cmd
    print(f"CSV: {content}")
    assert "'=cmd" in content
