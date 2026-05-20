from imednet.models.records import Record
from imednet.sdk import AsyncImednetSDK, ImednetSDK


def sync_record_signature() -> None:
    sdk = ImednetSDK(api_key="mock", security_key="mock")
    record: Record = sdk.records.get(study_key="STUDY", item_id="123")
    _ = record


async def async_record_signature() -> None:
    sdk = AsyncImednetSDK(api_key="mock", security_key="mock")
    record: Record = await sdk.records.async_get(study_key="STUDY", item_id="123")
    _ = record
