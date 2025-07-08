import os
from typing import Iterator

import pytest

from imednet.integrations import export
from imednet.sdk import ImednetSDK

API_KEY = os.getenv("IMEDNET_API_KEY")
SECURITY_KEY = os.getenv("IMEDNET_SECURITY_KEY")
BASE_URL = os.getenv("IMEDNET_BASE_URL")
RUN_E2E = os.getenv("IMEDNET_RUN_E2E") == "1"

pytestmark = pytest.mark.skipif(
    not RUN_E2E or not (API_KEY and SECURITY_KEY),
    reason=(
        "Set IMEDNET_RUN_E2E=1 and provide IMEDNET_API_KEY/IMEDNET_SECURITY_KEY to run live tests"
    ),
)


@pytest.fixture(scope="module")
def sdk() -> Iterator[ImednetSDK]:
    with ImednetSDK(api_key=API_KEY, security_key=SECURITY_KEY, base_url=BASE_URL) as client:
        yield client


@pytest.fixture(scope="module")
def study_key(sdk: ImednetSDK) -> str:
    studies = sdk.get_studies()
    if not studies:
        pytest.skip("No studies available for integration tests")
    return studies[0].study_key


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


def test_export_to_sql(sdk: ImednetSDK, study_key: str, tmp_path) -> None:
    pytest.importorskip("sqlalchemy")
    p = tmp_path / "db.sqlite"
    export.export_to_sql(sdk, study_key, "table", f"sqlite:///{p}")
    assert p.exists()


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
