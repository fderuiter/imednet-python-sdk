"""
Utility functions for live testing of the iMednet Python SDK.

This module provides helper functions for setting up tests with API credentials
and common testing utilities.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from imednet.sdk import ImednetSDK
from imednet_sdk import ImednetClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_credentials() -> Dict[str, Optional[str]]:
    """
    Load API credentials from environment variables or .env file.

    Returns:
        Dict containing API key, security key, and base URL
    """
    # Check for .env file at the root of the project
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        logger.info(f"Loading credentials from .env file: {env_path}")
        load_dotenv(env_path)
    else:
        logger.info("No .env file found, checking environment variables")
        load_dotenv()  # Will still check environment variables

    credentials = {
        "api_key": os.getenv("IMEDNET_API_KEY"),
        "security_key": os.getenv("IMEDNET_SECURITY_KEY"),
        "base_url": os.getenv("IMEDNET_BASE_URL"),
    }

    # Verify the credentials
    missing = [k for k, v in credentials.items() if not v]
    if missing:
        logger.warning(f"Missing credentials: {', '.join(missing)}")
    else:
        logger.info("Successfully loaded all required credentials")

    return credentials


def initialize_imednet_client(
    api_key: Optional[str] = None,
    security_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> ImednetClient:
    """
    Initialize an ImednetClient with the provided or environment credentials.

    Args:
        api_key: Optional explicit API key
        security_key: Optional explicit security key
        base_url: Optional explicit base URL

    Returns:
        Initialized ImednetClient
    """
    if not (api_key and security_key):
        credentials = load_credentials()
        api_key = api_key or credentials["api_key"]
        security_key = security_key or credentials["security_key"]
        base_url = base_url or credentials["base_url"]

    logger.info(f"Initializing ImednetClient with URL: {base_url}")
    return ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)


def initialize_imednet_sdk(
    api_key: Optional[str] = None, security_key: Optional[str] = None
) -> ImednetSDK:
    """
    Initialize an ImednetSDK instance with the provided or environment credentials.

    Args:
        api_key: Optional explicit API key
        security_key: Optional explicit security key    Returns:
        Initialized ImednetSDK
    """
    if not (api_key and security_key):
        credentials = load_credentials()
        api_key = api_key or credentials["api_key"]
        security_key = security_key or credentials["security_key"]

    if not api_key or not security_key:
        raise ValueError("API key and security key are required for ImednetSDK initialization")

    # Type assertions to satisfy mypy
    assert api_key is not None
    assert security_key is not None

    logger.info("Initializing ImednetSDK")
    return ImednetSDK(api_key=api_key, security_key=security_key)


def log_response(response: Any, label: str) -> None:
    """
    Log details of a response object in a structured way.

    Args:
        response: Response object to log
        label: Label to identify the response in logs
    """
    logger.info(f"--- {label} Response ---")

    if hasattr(response, "data") and response.data:
        if isinstance(response.data, list):
            logger.info(f"Retrieved {len(response.data)} items")
            # Log first item as sample if available
            if len(response.data) > 0:
                logger.info(f"Sample item: {response.data[0]}")
        else:
            logger.info(f"Data: {response.data}")
    else:
        logger.info(f"Response: {response}")
