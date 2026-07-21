"""Script to fix docstrings in the codebase."""

import argparse
import os


def process_file_export(filepath):
    if not os.path.isfile(filepath):
        print(f"Warning: File {filepath} not found.")
        return
    with open(filepath) as f:
        content = f.read()

    content = content.replace(
        "class TabularSinkConfig(SinkConfig):",
        'class TabularSinkConfig(SinkConfig):\n    """Configuration for tabular sinks."""',
    )
    content = content.replace(
        "class TabularCSVSink(ExportSink):",
        'class TabularCSVSink(ExportSink):\n    """Sink for exporting data to CSV format."""',
    )
    content = content.replace(
        "def __init__(self, path: str, config: Optional[TabularSinkConfig] = None):",
        'def __init__(self, path: str, config: Optional[TabularSinkConfig] = None):\n        """Initialize the CSV sink."""',
    )
    content = content.replace(
        "def write_batch(self, records: Sequence[Any], *, batch_id: str) -> int:",
        'def write_batch(self, records: Sequence[Any], *, batch_id: str) -> int:\n        """Write a batch of records to the sink."""',
    )
    content = content.replace(
        "def flush(self) -> None:", 'def flush(self) -> None:\n        """Flush the sink."""'
    )
    content = content.replace(
        "def close(self) -> None:", 'def close(self) -> None:\n        """Close the sink."""'
    )
    content = content.replace(
        "class TabularSQLSink(ExportSink):",
        'class TabularSQLSink(ExportSink):\n    """Sink for exporting data to SQL databases."""',
    )
    content = content.replace(
        "def __init__(self, table: str, engine: Any, config: Optional[TabularSinkConfig] = None):",
        'def __init__(self, table: str, engine: Any, config: Optional[TabularSinkConfig] = None):\n        """Initialize the SQL sink."""',
    )

    with open(filepath, "w") as f:
        f.write(content)


def process_file_job_poller(filepath):
    if not os.path.isfile(filepath):
        print(f"Warning: File {filepath} not found.")
        return
    with open(filepath) as f:
        content = f.read()

    content = content.replace(
        "def __init__(self, message: str, status: JobStatus) -> None:",
        'def __init__(self, message: str, status: JobStatus) -> None:\n        """Initialize the JobFailedError."""',
    )

    with open(filepath, "w") as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description="Fix hardcoded docstrings in specific files.")
    parser.add_argument(
        "targets",
        nargs="*",
        help="Target directories or files. Defaults to specific internal files.",
    )
    args = parser.parse_args()

    default_export = "packages/core/src/imednet/integrations/export.py"
    default_job_poller = "packages/core/src/imednet/utils/job_poller.py"

    if not args.targets:
        process_file_export(default_export)
        process_file_job_poller(default_job_poller)
    else:
        for target in args.targets:
            if os.path.isdir(target):
                for root, _, files in os.walk(target):
                    for file in files:
                        path = os.path.join(root, file)
                        if "export.py" in path:
                            process_file_export(path)
                        elif "job_poller.py" in path:
                            process_file_job_poller(path)
            elif os.path.isfile(target):
                if "export.py" in target:
                    process_file_export(target)
                elif "job_poller.py" in target:
                    process_file_job_poller(target)
            else:
                print(f"Warning: Target '{target}' not found or is invalid.")


if __name__ == '__main__':
    main()
