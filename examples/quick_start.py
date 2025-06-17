from __future__ import annotations

import os
import sys

from imednet import ImednetSDK
from imednet.utils import configure_json_logging

"""Quick start example using environment variables for authentication.

Set ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY`` before running this
script. Optionally set ``IMEDNET_BASE_URL`` for non-default instances.

Example:

    export IMEDNET_API_KEY="your_api_key"
    export IMEDNET_SECURITY_KEY="your_security_key"
    python examples/quick_start.py
"""


def main() -> None:
    """Run a minimal SDK example using environment variables."""

    configure_json_logging()

    missing = [var for var in ("IMEDNET_API_KEY", "IMEDNET_SECURITY_KEY") if not os.getenv(var)]
    if missing:
        vars_ = ", ".join(missing)
        print(f"Missing required environment variable(s): {vars_}", file=sys.stderr)
        sys.exit(1)

    sdk = ImednetSDK()
    print(sdk.studies.list())


if __name__ == "__main__":
    main()
