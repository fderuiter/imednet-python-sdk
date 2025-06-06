"""Example using AsyncImednetSDK to list studies."""

import asyncio
import os

from imednet.async_sdk import AsyncImednetSDK


async def main() -> None:
    async with AsyncImednetSDK(
        api_key=os.environ["IMEDNET_API_KEY"],
        security_key=os.environ["IMEDNET_SECURITY_KEY"],
        base_url=os.getenv("IMEDNET_BASE_URL"),
    ) as sdk:
        studies = await sdk.studies.list()
        print(studies)


if __name__ == "__main__":
    asyncio.run(main())
