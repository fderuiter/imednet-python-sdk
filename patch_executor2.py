import re

with open("src/imednet/core/http/executor.py", "r") as f:
    content = f.read()

# Add a NoReturn typing for _process_retry_error if it doesn't return
# Wait, it can return a response if e.last_attempt and not e.last_attempt.failed!
# However, mypy is complaining about `response = e.last_attempt.result()` because it doesn't know what it returns.

replacement_base = """
    def _process_retry_error(self, e: RetryError, monitor: RequestMonitor) -> httpx.Response:
        \"\"\"Handle RetryError, extracting successful result if present, else escalate.\"\"\"
        if e.last_attempt and not e.last_attempt.failed:
            response: httpx.Response = e.last_attempt.result()
            monitor.on_success(response)
            return handle_response(response)
        monitor.on_retry_error(e)
"""

pattern = r"    def _process_retry_error\(self, e: RetryError, monitor: RequestMonitor\) -> httpx\.Response:\n.*?(?=    @abstractmethod)"
content = re.sub(pattern, replacement_base, content, flags=re.DOTALL)

with open("src/imednet/core/http/executor.py", "w") as f:
    f.write(content)
