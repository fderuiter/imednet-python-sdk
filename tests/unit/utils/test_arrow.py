from datetime import datetime, timezone

import pyarrow as pa
from pydantic import BaseModel

from imednet.utils.arrow import to_arrow_table


def test_to_arrow_table_empty_records_returns_empty_table() -> None:
    table = to_arrow_table([])

    assert table.num_rows == 0
    assert table.num_columns == 0


def test_to_arrow_table_handles_key_variations_with_nulls() -> None:
    table = to_arrow_table([{"subject_key": "S1", "weight": 73.5}, {"subject_key": "S2"}])

    assert table.column("subject_key").to_pylist() == ["S1", "S2"]
    assert table.column("weight").to_pylist() == [73.5, None]
    assert table.schema.field("weight").type == pa.float64()


def test_to_arrow_table_preserves_datetime_bool_and_float_types() -> None:
    recorded_at = datetime(2025, 1, 1, 8, 30, tzinfo=timezone.utc)
    table = to_arrow_table(
        [
            {"recorded_at": recorded_at, "is_complete": True, "score": 1.25},
            {"recorded_at": None, "is_complete": False, "score": 2.5},
        ]
    )

    assert pa.types.is_timestamp(table.schema.field("recorded_at").type)
    assert table.schema.field("is_complete").type == pa.bool_()
    assert table.schema.field("score").type == pa.float64()


def test_to_arrow_table_accepts_pydantic_like_records() -> None:
    class Visit(BaseModel):
        subject_key: str
        completed: bool
        systolic: float | None = None

    schema = pa.schema(
        [
            pa.field("subject_key", pa.string()),
            pa.field("completed", pa.bool_()),
            pa.field("systolic", pa.float64()),
            pa.field("missing_vector", pa.null()),
        ]
    )
    table = to_arrow_table(
        [
            Visit(subject_key="S1", completed=True, systolic=120.0),
            Visit(subject_key="S2", completed=False),
        ],
        schema=schema,
    )

    assert table.column("subject_key").to_pylist() == ["S1", "S2"]
    assert table.column("completed").to_pylist() == [True, False]
    assert table.column("systolic").to_pylist() == [120.0, None]
    assert table.column("missing_vector").to_pylist() == [None, None]
    assert table.schema.field("missing_vector").type == pa.null()
