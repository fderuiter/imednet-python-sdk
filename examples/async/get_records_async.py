import asyncio
import os

from imednet.sdk import AsyncImednetSDK

"""Example script demonstrating basic usage of the AsyncImednetSDK.

This script initializes the asynchronous client with API credentials, retrieves a list of
studies, selects the first study, and then fetches and prints a few records associated with
that study.

Credentials default to the ``IMEDNET_*`` environment variables if set. Replace any
remaining ``XXXXXXXXXX`` placeholders for the study key. ``base_url`` can be left
``None`` to use the default iMednet endpoint or set to a custom URL if needed.
"""

api_key = os.getenv("IMEDNET_API_KEY", "XXXXXXXXXX")
security_key = os.getenv("IMEDNET_SECURITY_KEY", "XXXXXXXXXX")
base_url = os.getenv("IMEDNET_BASE_URL")
study_key = os.getenv("IMEDNET_STUDY_KEY", "XXXXXXXXXX")


async def main() -> None:
    try:
        async with AsyncImednetSDK(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
        ) as sdk:
            studies = await sdk.studies.async_list()
            if not studies:
                print("No studies returned from API.")
            for study in studies[:1]:
                study_key = study.study_key
                records = await sdk.records.async_list(study_key=study_key)
                print(f"Records for study '{study_key}': {len(records)}")
                for record in records[:5]:
                    print(f"- Record ID: {record.record_id}, " f"Subject Key: {record.subject_key}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
