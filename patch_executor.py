import re

with open("src/imednet/core/http/executor.py", "r") as f:
    content = f.read()

# I will replace SyncRequestExecutor and AsyncRequestExecutor with versions that use a helper
# method in BaseRequestExecutor to handle the retry result and monitoring uniformly.

base_addition = """
    def _handle_retry_result(self, retry_result: Any, monitor: RequestMonitor) -> httpx.Response:
        \"\"\"Extract the response from the retry execution and update the monitor.\"\"\"
        if isinstance(retry_result, RetryError):
            e = retry_result
            if e.last_attempt and not e.last_attempt.failed:
                response = e.last_attempt.result()
                monitor.on_success(response)
                return handle_response(response)
            else:
                monitor.on_retry_error(e)

        if retry_result is not None:
            monitor.on_success(retry_result)
            return handle_response(retry_result)

        raise RuntimeError("Request failed without response or exception")
"""

# Actually, the try/except block is around the retryer call.
# Let's extract the execution into a _execute_with_monitor function.

replacement_base = """class BaseRequestExecutor(ABC):
    \"\"\"Abstract base for request executors.\"\"\"

    def __init__(
        self,
        send: Any,
        retries: int,
        backoff_factor: float,
        tracer: Optional[Tracer] = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.send = send
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.tracer = tracer
        self.retry_policy = retry_policy or DefaultRetryPolicy()

    def _get_retry_predicate(self, method: str) -> Callable[[RetryCallState], bool]:
        \"\"\"Return a retry predicate that includes the HTTP method in state.\"\"\"
        policy = self.retry_policy

        def should_retry(retry_state: RetryCallState) -> bool:
            state = RetryState(
                attempt_number=retry_state.attempt_number,
                exception=(
                    retry_state.outcome.exception()
                    if retry_state.outcome and retry_state.outcome.failed
                    else None
                ),
                result=(
                    retry_state.outcome.result()
                    if retry_state.outcome and not retry_state.outcome.failed
                    else None
                ),
                method=method,
            )
            return policy.should_retry(state)

        return should_retry

    def _process_result(self, response: Optional[httpx.Response], monitor: RequestMonitor) -> httpx.Response:
        \"\"\"Process successful response or raise error if None.\"\"\"
        if response is not None:
            monitor.on_success(response)
            return handle_response(response)
        raise RuntimeError("Request failed without response or exception")

    def _process_retry_error(self, e: RetryError, monitor: RequestMonitor) -> httpx.Response:
        \"\"\"Handle RetryError, extracting successful result if present, else escalate.\"\"\"
        if e.last_attempt and not e.last_attempt.failed:
            response = e.last_attempt.result()
            monitor.on_success(response)
            return handle_response(response)
        monitor.on_retry_error(e)

    @abstractmethod
    def __call__(self, method: str, url: str, **kwargs: Any) -> Any:
        \"\"\"Execute the request.\"\"\"
"""

replacement_sync = """class SyncRequestExecutor(BaseRequestExecutor):
    \"\"\"Execute synchronous HTTP requests with retry and error handling.\"\"\"

    def __init__(
        self,
        send: Callable[..., httpx.Response],
        retries: int,
        backoff_factor: float,
        tracer: Optional[Tracer] = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        super().__init__(send, retries, backoff_factor, tracer, retry_policy)
        # self.send is set in super

    def __call__(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        def send_fn() -> httpx.Response:
            return self.send(method, url, **kwargs)

        retryer = Retrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self._get_retry_predicate(method),
            reraise=False,
        )

        with RequestMonitor(self.tracer, method, url) as monitor:
            try:
                response = retryer(send_fn)
                return self._process_result(response, monitor)
            except RetryError as e:
                return self._process_retry_error(e, monitor)
"""

replacement_async = """class AsyncRequestExecutor(BaseRequestExecutor):
    \"\"\"Execute asynchronous HTTP requests with retry and error handling.\"\"\"

    def __init__(
        self,
        send: Callable[..., Awaitable[httpx.Response]],
        retries: int,
        backoff_factor: float,
        tracer: Optional[Tracer] = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        super().__init__(send, retries, backoff_factor, tracer, retry_policy)
        # self.send is set in super

    async def __call__(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        async def send_fn() -> httpx.Response:
            return await self.send(method, url, **kwargs)

        retryer = AsyncRetrying(
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff_factor),
            retry=self._get_retry_predicate(method),
            reraise=False,
        )

        async with RequestMonitor(self.tracer, method, url) as monitor:
            try:
                response = await retryer(send_fn)
                return self._process_result(response, monitor)
            except RetryError as e:
                return self._process_retry_error(e, monitor)
"""

def replace_class(text, class_name, replacement):
    pattern = r"class " + class_name + r"\(.*?\):\n.*?(?=class |$)"
    return re.sub(pattern, replacement, text, flags=re.DOTALL)

with open("src/imednet/core/http/executor.py", "w") as f:
    # First replace BaseRequestExecutor
    content = replace_class(content, "BaseRequestExecutor", replacement_base)
    # Then Sync
    content = replace_class(content, "SyncRequestExecutor", replacement_sync)
    # Then Async
    content = replace_class(content, "AsyncRequestExecutor", replacement_async)
    f.write(content)
