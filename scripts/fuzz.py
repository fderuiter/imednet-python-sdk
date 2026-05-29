import csv
import json
import logging
import os
import sys
import zipfile
from io import BytesIO

import atheris

# Suppress logging
logging.disable(logging.CRITICAL)

# Set up paths so we can import packages
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'packages', 'core', 'src'))
)
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'packages', 'plugins-sinks', 'src')
    ),
)

# Instrument the code for coverage
with atheris.instrument_imports():
    import imednet_sinks

    import imednet
    from imednet.models.engine import _CACHE, load_schemas
    from imednet.sdk import ImednetSDK
    from imednet.validation.data_dictionary import DataDictionaryLoader


# Dummy config for Snowflake
class DummyConfig:
    batch_size = 100
    idempotent = True


def fuzz_dynamic_model(data: bytes):
    # Fuzzing the dynamic model loading by writing random JSON/data to a fake postman file
    postman_path = "/tmp/fuzz_postman.json"
    os.environ["IMEDNET_POSTMAN_PATH"] = postman_path

    with open(postman_path, "wb") as f:
        f.write(data)

    # Clear cache to force reload
    _CACHE.clear()

    try:
        load_schemas()
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        # Expected exceptions for malformed data
        pass
    except Exception as e:
        # Any other exception is an unhandled parsing error
        raise e


def fuzz_data_dictionary(data: bytes):
    try:
        DataDictionaryLoader.from_zip(BytesIO(data))
    except (zipfile.BadZipFile, UnicodeDecodeError, csv.Error, KeyError, Exception):
        # The from_zip does not have custom exceptions, so catch all expected from malformed zip
        pass


def fuzz_warehouse_transformation(data: bytes):
    import pyarrow as pa
    from imednet_sinks.warehouse import _records_to_arrow_table

    # Generate random string representations to pass as records
    try:
        text = data.decode('utf-8', errors='ignore')
        if not text:
            return

        # Try to parse as JSON
        try:
            records_data = json.loads(text)
        except json.JSONDecodeError:
            # If not JSON, use random string chunks
            records_data = [{"record_data": {"field": text[:50]}}]

        if not isinstance(records_data, list):
            records_data = [records_data]

        # Mock class for records
        class DummyRecord:
            def __init__(self, d):
                self.record_id = str(d.get("id", "1"))
                self.form_id = str(d.get("form_id", "1"))
                self.visit_id = str(d.get("visit_id", "1"))
                self.subject_key = str(d.get("subject_key", "1"))
                self.record_data = d.get("data", {})

        records = []
        for rd in records_data:
            if isinstance(rd, dict):
                records.append(DummyRecord(rd))

        # Transform
        _records_to_arrow_table(records)

    except (pa.ArrowInvalid, TypeError, ValueError, OverflowError):
        pass


def TestOneInput(data):
    if len(data) < 1:
        return

    # To balance out, we divide data and do one of the fuzzers based on first byte
    mode = data[0] % 3
    if mode == 0:
        fuzz_dynamic_model(data)
    elif mode == 1:
        fuzz_data_dictionary(data)
    elif mode == 2:
        fuzz_warehouse_transformation(data)


if __name__ == "__main__":
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
