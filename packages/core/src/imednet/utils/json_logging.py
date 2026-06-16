import logging

from imednet.security import RedactionLogFilter

try:  # python-json-logger >= 3.0
    from pythonjsonlogger.json import JsonFormatter
except ModuleNotFoundError:  # pragma: no cover - fallback for older versions
    from pythonjsonlogger.jsonlogger import JsonFormatter


def configure_json_logging(level: int = logging.INFO) -> None:
    """Configure root logger to emit JSON formatted logs."""
    handler = logging.StreamHandler()
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    
    redaction_filter = RedactionLogFilter()
    handler.addFilter(redaction_filter)
    
    logging.basicConfig(level=level, handlers=[handler], force=True)
