import asyncio

import pytest

from imednet.core.context import get_current_study, set_study_context


async def async_worker(study_key: str, delay: float) -> str:
    set_study_context(study_key)
    await asyncio.sleep(delay)
    return get_current_study()


@pytest.mark.asyncio
async def test_contextvars_prevents_race_conditions() -> None:
    results = await asyncio.gather(
        async_worker("STUDY-A", 0.2),
        async_worker("STUDY-B", 0.1),
        async_worker("STUDY-C", 0.3),
    )
    assert results == ["STUDY-A", "STUDY-B", "STUDY-C"]
