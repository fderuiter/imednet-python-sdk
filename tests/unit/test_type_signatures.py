"""Static type-signature checks consumed by mypy (not runtime pytest cases)."""

from typing import cast

from imednet.models.records import Record
from imednet.sdk import AsyncImednetSDK, ImednetSDK


def sync_record_signature() -> None:
    """Test sync_record_signature behavior."""
    sdk = cast(ImednetSDK, object())
    record: Record = sdk.records.get(study_key="STUDY", item_id="123")
    _ = record


async def async_record_signature() -> None:
    """Implementation detail."""
    sdk = cast(AsyncImednetSDK, object())
    record: Record = await sdk.records.async_get(study_key="STUDY", item_id="123")
    _ = record
