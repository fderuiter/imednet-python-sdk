import logging

from pythonjsonlogger import jsonlogger


def configure_json_logging(level: int = logging.INFO) -> None:
    """Configure root logger to emit JSON formatted logs."""
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    handler.setFormatter(formatter)
    logging.basicConfig(level=level, handlers=[handler], force=True)
