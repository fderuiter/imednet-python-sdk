import sys
from types import ModuleType
from unittest.mock import MagicMock

import pandas as pd
import pytest

import imednet.integrations.export as export_mod


def _setup_mapper(monkeypatch):
    df = MagicMock()
    mapper_inst = MagicMock()
    mapper_inst.dataframe.return_value = df
    mapper_cls = MagicMock(return_value=mapper_inst)
    monkeypatch.setattr(export_mod, "RecordMapper", mapper_cls)
    return df, mapper_cls, mapper_inst


def _setup_real_mapper(monkeypatch):
    df = pd.DataFrame({"A": [1]})
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
    engine = MagicMock()
    engine.dialect.name = "sqlite"
    create_engine = MagicMock(return_value=engine)
    sa_module.create_engine = create_engine
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)

    export_mod.export_to_sql(sdk, "STUDY", "table", "sqlite://", if_exists="append")

    mapper_cls.assert_called_once_with(sdk)
    mapper_inst.dataframe.assert_called_once_with("STUDY", use_labels_as_columns=False)
    create_engine.assert_called_once_with("sqlite://")
    df.to_sql.assert_called_once_with("table", engine, if_exists="append", index=False)


def test_export_functions_handle_duplicate_columns(tmp_path, monkeypatch):
    df = pd.DataFrame([[1, 2]], columns=["A", "A"])
    monkeypatch.setattr(
        pd.DataFrame,
        "to_parquet",
        lambda self, path, index=False, **kwargs: open(path, "wb").close(),
    )
    mapper_cls = MagicMock(return_value=MagicMock(dataframe=MagicMock(return_value=df)))
    monkeypatch.setattr(export_mod, "RecordMapper", mapper_cls)
    sdk = MagicMock()

    out_json = tmp_path / "d.json"
    export_mod.export_to_json(sdk, "S", str(out_json))
    assert out_json.exists()

    out_db = tmp_path / "d.db"
    export_mod.export_to_sql(sdk, "S", "t", f"sqlite:///{out_db}")
    assert out_db.exists()

    out_parquet = tmp_path / "d.parquet"
    export_mod.export_to_parquet(sdk, "S", str(out_parquet))
    assert out_parquet.exists()


def test_export_functions_handle_case_insensitive_duplicates(tmp_path, monkeypatch):
    df = pd.DataFrame([[1, 2]], columns=["A", "a"])
    monkeypatch.setattr(
        pd.DataFrame,
        "to_parquet",
        lambda self, path, index=False, **kwargs: open(path, "wb").close(),
    )
    mapper_cls = MagicMock(return_value=MagicMock(dataframe=MagicMock(return_value=df)))
    monkeypatch.setattr(export_mod, "RecordMapper", mapper_cls)
    sdk = MagicMock()

    out_json = tmp_path / "case.json"
    export_mod.export_to_json(sdk, "S", str(out_json))
    assert out_json.exists()

    out_db = tmp_path / "case.db"
    export_mod.export_to_sql(sdk, "S", "t", f"sqlite:///{out_db}")
    assert out_db.exists()

    out_parquet = tmp_path / "case.parquet"
    export_mod.export_to_parquet(sdk, "S", str(out_parquet))
    assert out_parquet.exists()


def test_export_sql_too_many_columns(monkeypatch):
    columns = [f"c{i}" for i in range(2001)]
    df = pd.DataFrame([range(2001)], columns=columns)
    monkeypatch.setattr(pd.DataFrame, "to_sql", MagicMock())
    mapper_cls = MagicMock(return_value=MagicMock(dataframe=MagicMock(return_value=df)))
    monkeypatch.setattr(export_mod, "RecordMapper", mapper_cls)

    engine = MagicMock()
    engine.dialect.name = "sqlite"
    sa_module = ModuleType("sqlalchemy")
    sa_module.create_engine = MagicMock(return_value=engine)
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)

    with pytest.raises(ValueError, match="SQLite supports up to 2000 columns"):
        export_mod.export_to_sql(MagicMock(), "STUDY", "table", "sqlite://")
    pd.DataFrame.to_sql.assert_not_called()


def test_export_to_sql_by_form(monkeypatch):
    sdk = MagicMock()
    form1 = MagicMock(form_id=1, form_key="F1")
    form2 = MagicMock(form_id=2, form_key="F2")
    sdk.forms.list.return_value = [form1, form2]
    sdk.variables.list.side_effect = [
        [MagicMock(variable_name="A", label="A")],
        [MagicMock(variable_name="B", label="B")],
    ]

    mapper_inst = MagicMock()
    mapper_inst._build_record_model.return_value = object()
    mapper_inst._fetch_records.side_effect = [MagicMock(), MagicMock()]
    mapper_inst._parse_records.side_effect = [([], 0), ([], 0)]
    df1 = MagicMock()
    df2 = MagicMock()
    mapper_inst._build_dataframe.side_effect = [df1, df2]
    mapper_cls = MagicMock(return_value=mapper_inst)
    monkeypatch.setattr(export_mod, "RecordMapper", mapper_cls)

    sa_module = ModuleType("sqlalchemy")
    engine = MagicMock()
    engine.dialect.name = "sqlite"
    create_engine = MagicMock(return_value=engine)
    sa_module.create_engine = create_engine
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)

    export_mod.export_to_sql_by_form(sdk, "STUDY", "sqlite://")

    mapper_cls.assert_called_once_with(sdk)
    assert sdk.variables.list.call_count == 2
    df1.to_sql.assert_called_once_with("F1", engine, if_exists="replace", index=False)
    df2.to_sql.assert_called_once_with("F2", engine, if_exists="replace", index=False)
