from __future__ import annotations

import sys

from imednet import ImednetSDK, load_config
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

    try:
        cfg = load_config()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    sdk = ImednetSDK(
        api_key=cfg.api_key,
        security_key=cfg.security_key,
        base_url=cfg.base_url,
    )
    print(sdk.studies.list())


if __name__ == "__main__":
    main()
