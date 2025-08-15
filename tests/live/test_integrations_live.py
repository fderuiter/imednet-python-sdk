import pandas as pd
import pytest

from imednet.integrations import export
from imednet.sdk import ImednetSDK


def test_export_to_csv(sdk: ImednetSDK, study_key: str, tmp_path) -> None:
    p = tmp_path / "out.csv"
    export.export_to_csv(sdk, study_key, str(p))
    assert p.exists()


def test_export_to_excel(sdk: ImednetSDK, study_key: str, tmp_path) -> None:
    pytest.importorskip("openpyxl")
    p = tmp_path / "out.xlsx"
    export.export_to_excel(sdk, study_key, str(p))
    assert p.exists()


def test_export_to_json(sdk: ImednetSDK, study_key: str, tmp_path) -> None:
    p = tmp_path / "out.json"
    export.export_to_json(sdk, study_key, str(p))
    assert p.exists()


def test_export_to_parquet(sdk: ImednetSDK, study_key: str, tmp_path) -> None:
    pytest.importorskip("pyarrow")
    p = tmp_path / "out.parquet"
    export.export_to_parquet(sdk, study_key, str(p))
    assert p.exists()


def test_export_to_sql_handles_column_limit(
    sdk: ImednetSDK, study_key: str, tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("sqlalchemy")
    from sqlalchemy import create_engine, inspect, text

    p = tmp_path / "db.sqlite"
    columns = [f"c{i}" for i in range(export.MAX_SQLITE_COLUMNS + 1)]
    df = pd.DataFrame({c: [i] for i, c in enumerate(columns)})
    monkeypatch.setattr(export, "_records_df", lambda *a, **k: df)
    export.export_to_sql(sdk, study_key, "table", f"sqlite:///{p}")
    assert p.exists()
    engine = create_engine(f"sqlite:///{p}")
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    assert "table_part1" in table_names
    assert "table_part2" in table_names
    with engine.connect() as conn:
        for t in ("table_part1", "table_part2"):
            count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            assert count == 1


def test_imednet_hook() -> None:
    pytest.importorskip("airflow")
    from imednet.integrations.airflow import ImednetHook

    hook = ImednetHook()
    conn = hook.get_conn()
    assert isinstance(conn, ImednetSDK)


def test_imednet_export_operator(study_key: str, tmp_path) -> None:
    pytest.importorskip("airflow")
    from imednet.integrations.airflow import ImednetExportOperator  # type: ignore[attr-defined]

    op = ImednetExportOperator(study_key=study_key, output_path=str(tmp_path / "x.csv"))
    assert op.execute({})


def test_imednet_to_s3_operator(study_key: str) -> None:
    pytest.importorskip("airflow")
    from imednet.integrations.airflow import ImednetToS3Operator  # type: ignore[attr-defined]

    op = ImednetToS3Operator(study_key=study_key, s3_bucket="bucket", s3_key="key")
    assert op.execute({}) == "key"


def test_imednet_job_sensor(study_key: str) -> None:
    pytest.importorskip("airflow")
    from imednet.integrations.airflow import ImednetJobSensor  # type: ignore[attr-defined]

    sensor = ImednetJobSensor(study_key=study_key, batch_id="ID")
    with pytest.raises(Exception):
        sensor.poke({})
