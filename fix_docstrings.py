import os

with open("packages/core/src/imednet/integrations/export.py", "r") as f:
    content = f.read()

content = content.replace(
    "class TabularSinkConfig(SinkConfig):",
    'class TabularSinkConfig(SinkConfig):\n    """Configuration for tabular sinks."""'
)
content = content.replace(
    "class TabularCSVSink(ExportSink):",
    'class TabularCSVSink(ExportSink):\n    """Sink for exporting data to CSV format."""'
)
content = content.replace(
    "def __init__(self, path: str, config: Optional[TabularSinkConfig] = None):",
    'def __init__(self, path: str, config: Optional[TabularSinkConfig] = None):\n        """Initialize the CSV sink."""'
)
content = content.replace(
    "def write_batch(self, records: Sequence[Any], *, batch_id: str) -> int:",
    'def write_batch(self, records: Sequence[Any], *, batch_id: str) -> int:\n        """Write a batch of records to the sink."""'
)
content = content.replace(
    "def flush(self) -> None:",
    'def flush(self) -> None:\n        """Flush the sink."""'
)
content = content.replace(
    "def close(self) -> None:",
    'def close(self) -> None:\n        """Close the sink."""'
)
content = content.replace(
    "class TabularSQLSink(ExportSink):",
    'class TabularSQLSink(ExportSink):\n    """Sink for exporting data to SQL databases."""'
)
content = content.replace(
    "def __init__(self, table: str, engine: Any, config: Optional[TabularSinkConfig] = None):",
    'def __init__(self, table: str, engine: Any, config: Optional[TabularSinkConfig] = None):\n        """Initialize the SQL sink."""'
)

with open("packages/core/src/imednet/integrations/export.py", "w") as f:
    f.write(content)

with open("packages/core/src/imednet/utils/job_poller.py", "r") as f:
    content = f.read()

content = content.replace(
    "def __init__(self, message: str, status: JobStatus) -> None:",
    'def __init__(self, message: str, status: JobStatus) -> None:\n        """Initialize the JobFailedError."""'
)

with open("packages/core/src/imednet/utils/job_poller.py", "w") as f:
    f.write(content)
