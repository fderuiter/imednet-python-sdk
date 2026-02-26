# Examples

This directory contains examples demonstrating how to use the iMednet Python SDK.

## Prerequisites

Before running the examples, you need to set up your environment with your iMednet API credentials.

1.  Copy `.env.example` to `.env` in the root of the project:
    ```bash
    cp .env.example .env
    ```

2.  Fill in your API credentials in `.env`:
    ```ini
    IMEDNET_API_KEY=your_api_key_here
    IMEDNET_SECURITY_KEY=your_security_key_here
    # Optional: Set base URL if using a custom instance
    # IMEDNET_BASE_URL=https://edc.prod.imednetapi.com
    ```

## Running Examples

You can run any example directly using Python:

```bash
python examples/basic/get_studies.py
```

## Structure

-   `basic/`: Simple synchronous examples for common endpoints (studies, sites, subjects, records, etc.).
-   `async/`: Asynchronous examples using `asyncio`.
-   `workflows/`: Examples of higher-level workflows.
