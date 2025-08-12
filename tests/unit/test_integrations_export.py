import sys
from datetime import datetime
from types import ModuleType
from unittest.mock import MagicMock

import pandas as pd

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
    mapper_inst.dataframe.assert_called_once_with(
        "STUDY",
        use_labels_as_columns=False,
        variable_whitelist=None,
        form_whitelist=None,
    )
    df.to_csv.assert_called_once_with("out.csv", index=False, sep=";")


def test_export_to_excel(monkeypatch):
    df, mapper_cls, mapper_inst = _setup_mapper(monkeypatch)
    sdk = MagicMock()

    export_mod.export_to_excel(sdk, "STUDY", "out.xlsx")

    mapper_cls.assert_called_once_with(sdk)
    mapper_inst.dataframe.assert_called_once_with(
        "STUDY",
        use_labels_as_columns=False,
        variable_whitelist=None,
        form_whitelist=None,
    )
    df.to_excel.assert_called_once_with("out.xlsx", index=False)


def test_export_to_json(monkeypatch):
    df, mapper_cls, mapper_inst = _setup_mapper(monkeypatch)
    sdk = MagicMock()

    export_mod.export_to_json(sdk, "STUDY", "out.json", orient="records")

    mapper_cls.assert_called_once_with(sdk)
    mapper_inst.dataframe.assert_called_once_with(
        "STUDY",
        use_labels_as_columns=False,
        variable_whitelist=None,
        form_whitelist=None,
    )
    df.to_json.assert_called_once_with("out.json", orient="records", index=False)


def test_export_to_parquet(monkeypatch):
    df, mapper_cls, mapper_inst = _setup_mapper(monkeypatch)
    sdk = MagicMock()

    export_mod.export_to_parquet(sdk, "STUDY", "out.parquet", compression="snappy")

    mapper_cls.assert_called_once_with(sdk)
    mapper_inst.dataframe.assert_called_once_with(
        "STUDY",
        use_labels_as_columns=False,
        variable_whitelist=None,
        form_whitelist=None,
    )
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
    mapper_inst.dataframe.assert_called_once_with(
        "STUDY",
        use_labels_as_columns=False,
        variable_whitelist=None,
        form_whitelist=None,
    )
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
    columns = [f"c{i}" for i in range(export_mod.MAX_SQLITE_COLUMNS + 1)]
    df = pd.DataFrame(
        [range(export_mod.MAX_SQLITE_COLUMNS + 1)],
        columns=columns,
    )
    mock_to_sql = MagicMock()
    monkeypatch.setattr(pd.DataFrame, "to_sql", mock_to_sql)
    mapper_cls = MagicMock(return_value=MagicMock(dataframe=MagicMock(return_value=df)))
    monkeypatch.setattr(export_mod, "RecordMapper", mapper_cls)

    engine = MagicMock()
    engine.dialect.name = "sqlite"
    sa_module = ModuleType("sqlalchemy")
    sa_module.create_engine = MagicMock(return_value=engine)
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)

    export_mod.export_to_sql(MagicMock(), "STUDY", "table", "sqlite://")
    assert mock_to_sql.call_count == 2
    calls = mock_to_sql.call_args_list
    assert calls[0].args[0] == "table_part1"
    assert calls[1].args[0] == "table_part2"


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


def test_export_to_long_sql(monkeypatch):
    sdk = MagicMock()
    dt1 = datetime(2023, 1, 1)
    dt2 = datetime(2023, 1, 2)
    dt3 = datetime(2023, 1, 3)
    records = [
        MagicMock(record_id=1, form_id=10, record_data={"A": 1, "B": 2}, date_modified=dt1),
        MagicMock(record_id=2, form_id=11, record_data={"C": 3}, date_modified=dt2),
        MagicMock(record_id=3, form_id=12, record_data={"D": 4}, date_modified=dt3),
    ]
    mapper_inst = MagicMock(_fetch_records=MagicMock(return_value=records))
    mapper_cls = MagicMock(return_value=mapper_inst)
    monkeypatch.setattr(export_mod, "RecordMapper", mapper_cls)

    sa_module = ModuleType("sqlalchemy")
    engine = MagicMock()
    sa_module.create_engine = MagicMock(return_value=engine)
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)

    captured = []

    def fake_to_sql(self, table, engine_arg, if_exists, index=False):
        captured.append((self.copy(), if_exists))

    monkeypatch.setattr(pd.DataFrame, "to_sql", fake_to_sql)

    export_mod.export_to_long_sql(sdk, "STUDY", "tbl", "sqlite://", chunk_size=2)

    assert len(captured) == 2
    assert list(captured[0][0].to_dict("records")) == [
        {"record_id": 1, "form_id": 10, "variable_name": "A", "value": 1, "timestamp": dt1},
        {"record_id": 1, "form_id": 10, "variable_name": "B", "value": 2, "timestamp": dt1},
    ]
    assert captured[0][1] == "replace"
    assert list(captured[1][0].to_dict("records")) == [
        {"record_id": 2, "form_id": 11, "variable_name": "C", "value": 3, "timestamp": dt2},
        {"record_id": 3, "form_id": 12, "variable_name": "D", "value": 4, "timestamp": dt3},
    ]
    assert captured[1][1] == "append"
