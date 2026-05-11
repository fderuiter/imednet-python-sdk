import asyncio

import pytest

from imednet.core.context import get_current_study, reset_study_context, set_study_context


async def async_worker(study_key: str, delay: float) -> str:
    token = set_study_context(study_key)
    try:
        await asyncio.sleep(delay)
        return get_current_study()
    finally:
        reset_study_context(token)


@pytest.mark.asyncio
async def test_contextvars_prevents_race_conditions() -> None:
    results = await asyncio.gather(
        async_worker("STUDY-A", 0.2),
        async_worker("STUDY-B", 0.1),
        async_worker("STUDY-C", 0.3),
    )
    assert results == ["STUDY-A", "STUDY-B", "STUDY-C"]
