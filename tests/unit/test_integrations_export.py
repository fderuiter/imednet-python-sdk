import sys
from types import ModuleType
from unittest.mock import MagicMock

import imednet.integrations.export as export_mod


def _setup_mapper(monkeypatch):
    df = MagicMock()
    mapper_inst = MagicMock()
    mapper_inst.dataframe.return_value = df
    mapper_cls = MagicMock(return_value=mapper_inst)
    monkeypatch.setattr(export_mod, "RecordMapper", mapper_cls)
    return df, mapper_cls, mapper_inst


def test_export_to_csv(monkeypatch):
    df, mapper_cls, mapper_inst = _setup_mapper(monkeypatch)
    sdk = MagicMock()

    export_mod.export_to_csv(sdk, "STUDY", "out.csv", sep=";")

    mapper_cls.assert_called_once_with(sdk)
    mapper_inst.dataframe.assert_called_once_with("STUDY", use_labels_as_columns=False)
    df.to_csv.assert_called_once_with("out.csv", index=False, sep=";")


def test_export_to_excel(monkeypatch):
    df, mapper_cls, mapper_inst = _setup_mapper(monkeypatch)
    sdk = MagicMock()

    export_mod.export_to_excel(sdk, "STUDY", "out.xlsx")

    mapper_cls.assert_called_once_with(sdk)
    mapper_inst.dataframe.assert_called_once_with("STUDY", use_labels_as_columns=False)
    df.to_excel.assert_called_once_with("out.xlsx", index=False)


def test_export_to_json(monkeypatch):
    df, mapper_cls, mapper_inst = _setup_mapper(monkeypatch)
    sdk = MagicMock()

    export_mod.export_to_json(sdk, "STUDY", "out.json", orient="records")

    mapper_cls.assert_called_once_with(sdk)
    mapper_inst.dataframe.assert_called_once_with("STUDY", use_labels_as_columns=False)
    df.to_json.assert_called_once_with("out.json", orient="records", index=False)


def test_export_to_parquet(monkeypatch):
    df, mapper_cls, mapper_inst = _setup_mapper(monkeypatch)
    sdk = MagicMock()

    export_mod.export_to_parquet(sdk, "STUDY", "out.parquet", compression="snappy")

    mapper_cls.assert_called_once_with(sdk)
    mapper_inst.dataframe.assert_called_once_with("STUDY", use_labels_as_columns=False)
    df.to_parquet.assert_called_once_with("out.parquet", index=False, compression="snappy")


def test_export_to_sql(monkeypatch):
    df, mapper_cls, mapper_inst = _setup_mapper(monkeypatch)
    sdk = MagicMock()

    sa_module = ModuleType("sqlalchemy")
    create_engine = MagicMock(return_value="engine")
    sa_module.create_engine = create_engine
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)

    export_mod.export_to_sql(sdk, "STUDY", "table", "sqlite://", if_exists="append")

    mapper_cls.assert_called_once_with(sdk)
    mapper_inst.dataframe.assert_called_once_with("STUDY", use_labels_as_columns=False)
    create_engine.assert_called_once_with("sqlite://")
    df.to_sql.assert_called_once_with("table", "engine", if_exists="append", index=False)
