from __future__ import annotations

import os
import sys
from collections.abc import Iterator

import httpx

from imednet.core.client import Client
from imednet.core.exceptions import RateLimitError, ServerError
from imednet.core.retry import RetryPolicy, RetryState
from imednet.utils import configure_json_logging

"""Demonstrate custom retry logic with simulated rate limit and server errors.

The script uses a mock transport that returns a 429, then a 500, before
succeeding. Set ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY`` to any value
before running this script.

Example:

    export IMEDNET_API_KEY="dummy"
    export IMEDNET_SECURITY_KEY="dummy"
    python examples/custom_retry.py
"""


class RateLimitServerRetry(RetryPolicy):
    def should_retry(self, state: RetryState) -> bool:
        if isinstance(state.exception, (RateLimitError, ServerError)):
            return True
        if isinstance(state.result, httpx.Response):
            status = state.result.status_code
            return status == 429 or 500 <= status < 600
        return False


responses: Iterator[httpx.Response] = iter(
    [
        httpx.Response(429, json={"metadata": {"status": "TOO_MANY_REQUESTS"}}),
        httpx.Response(500, json={"metadata": {"status": "SERVER_ERROR"}}),
        httpx.Response(200, json={"data": "ok"}),
    ]
)


def responder(_: httpx.Request) -> httpx.Response:
    return next(responses)


class MockClient(Client):
    def _create_client(self, api_key: str, security_key: str) -> httpx.Client:  # type: ignore[override]
        return httpx.Client(
            base_url=self.base_url,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "x-imn-security-key": security_key,
            },
            timeout=self.timeout,
            transport=httpx.MockTransport(responder),
        )


def main() -> None:
    """Run a request with custom retry logic."""
    configure_json_logging()

    missing = [var for var in ("IMEDNET_API_KEY", "IMEDNET_SECURITY_KEY") if not os.getenv(var)]
    if missing:
        vars_ = ", ".join(missing)
        print(f"Missing required environment variable(s): {vars_}", file=sys.stderr)
        sys.exit(1)

    client = MockClient(
        os.environ["IMEDNET_API_KEY"],
        os.environ["IMEDNET_SECURITY_KEY"],
        retries=3,
        backoff_factor=0.01,
        retry_policy=RateLimitServerRetry(),
    )

    try:
        client.get("/studies")
    except RateLimitError:
        print("Request failed with rate limit error", file=sys.stderr)
    except ServerError:
        print("Request failed with server error", file=sys.stderr)
    else:
        print("Request succeeded")


if __name__ == "__main__":
    main()
