from __future__ import annotations

import asyncio
import os
import sys

from imednet import AsyncImednetSDK, load_config
from imednet.utils import configure_json_logging

"""Async quick start example using environment variables for authentication.

Set ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY`` before running this
script. Optionally set ``IMEDNET_BASE_URL`` for non-default instances.
Provide ``IMEDNET_JOB_STUDY_KEY`` and ``IMEDNET_BATCH_ID`` to poll a job.

Example::

    export IMEDNET_API_KEY="your_api_key"
    export IMEDNET_SECURITY_KEY="your_security_key"
    python examples/async_quick_start.py
"""


async def main() -> None:
    """Run a minimal async SDK example using environment variables."""
    configure_json_logging()

    try:
        cfg = load_config()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    async with AsyncImednetSDK(
        api_key=cfg.api_key,
        security_key=cfg.security_key,
        base_url=cfg.base_url,
    ) as sdk:
        studies = await sdk.studies.async_list()
        print(studies)

        job_study = os.getenv("IMEDNET_JOB_STUDY_KEY")
        batch_id = os.getenv("IMEDNET_BATCH_ID")
        if job_study and batch_id:
            status = await sdk.async_poll_job(job_study, batch_id, interval=2, timeout=60)
            print(status)


if __name__ == "__main__":
    asyncio.run(main())
