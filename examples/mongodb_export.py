"""Export study records to MongoDB.

Requires:
    pip install 'imednet[mongodb]'

Usage::

    python examples/mongodb_export.py
"""

from __future__ import annotations

import os

from imednet import ImednetSDK
from imednet.integrations import SinkConfig, export_to_mongodb

sdk = ImednetSDK(
    api_key=os.environ["IMEDNET_API_KEY"],
    security_key=os.environ.get("IMEDNET_SECURITY_KEY", ""),
)

STUDY_KEY = os.environ.get("IMEDNET_STUDY_KEY", "MY_STUDY")
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE", "imednet")
MONGODB_COLLECTION = os.environ.get("MONGODB_COLLECTION", "records")

rows_loaded = export_to_mongodb(
    sdk,
    STUDY_KEY,
    MONGODB_URI,
    MONGODB_DATABASE,
    MONGODB_COLLECTION,
    config=SinkConfig(batch_size=500, idempotent=True),
)
print(f"Loaded {rows_loaded} rows from study '{STUDY_KEY}' into MongoDB.")
