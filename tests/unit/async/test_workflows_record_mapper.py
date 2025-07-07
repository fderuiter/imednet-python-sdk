from unittest.mock import AsyncMock, MagicMock
from imednet.sdk import AsyncImednetSDK


class FakeAsyncSDK(AsyncImednetSDK):
    def __init__(self) -> None:  # pragma: no cover - simplified
        pass


import pandas as pd
import pytest
from imednet.models.records import Record
from imednet.models.variables import Variable
from imednet.workflows.record_mapper import RecordMapper


@pytest.mark.asyncio
async def test_dataframe_async() -> None:
    sdk = FakeAsyncSDK()
    sdk.variables = MagicMock()
    sdk.records = MagicMock()
    sdk.variables.async_list = AsyncMock(
        return_value=[Variable(variable_name="VAR", label="L", form_id=1)]
    )
    record = Record(
        record_id=1,
        subject_key="S",
        visit_id=1,
        form_id=1,
        record_status="C",
        record_data={"VAR": "x"},
    )
    sdk.records.async_list = AsyncMock(return_value=[record])

    mapper = RecordMapper(sdk)
    df = await mapper.dataframe("STUDY")

    sdk.variables.async_list.assert_awaited_once_with(study_key="STUDY")
    sdk.records.async_list.assert_awaited_once()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
