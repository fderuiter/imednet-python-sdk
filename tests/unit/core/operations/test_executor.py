"""TODO: Add docstring."""
import pytest

from imednet.core.operations.circuit_breaker import get_global_circuit_breaker
from imednet.core.operations.executor import UniversalExecutor
from imednet.core.operations.protocols import OperationProtocol


class RESTTask(OperationProtocol[str]):
    """TODO: Add docstring."""
    def __init__(self, fail_times=0):
        """TODO: Add docstring."""
        self.fail_times = fail_times
        self.attempts = 0

    def execute(self) -> str:
        """TODO: Add docstring."""
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise ValueError("HTTP Error")
        return "REST Success"


class NonRESTTask(OperationProtocol[str]):
    """TODO: Add docstring."""
    def __init__(self, fail_times=0):
        """TODO: Add docstring."""
        self.fail_times = fail_times
        self.attempts = 0

    def execute(self) -> str:
        """TODO: Add docstring."""
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise RuntimeError("DB Error")
        return "Non-REST Success"


def test_universal_executor_supports_rest_and_non_rest():
    """TODO: Add docstring."""
    get_global_circuit_breaker().reset()
    executor = UniversalExecutor(retries=2, backoff_factor=0.01)

    rest_task = RESTTask(fail_times=1)
    result = executor.execute(rest_task.execute)
    assert result == "REST Success"
    assert rest_task.attempts == 2

    non_rest_task = NonRESTTask(fail_times=1)
    result = executor.execute(non_rest_task.execute)
    assert result == "Non-REST Success"
    assert non_rest_task.attempts == 2


def test_universal_executor_fails_after_retries():
    """TODO: Add docstring."""
    get_global_circuit_breaker().reset()
    executor = UniversalExecutor(retries=1, backoff_factor=0.01)

    task = RESTTask(fail_times=5)
    with pytest.raises(ValueError, match="HTTP Error"):
        executor.execute(task.execute)
    assert task.attempts == 2


@pytest.mark.asyncio
async def test_universal_executor_async():
    """TODO: Add docstring."""
    get_global_circuit_breaker().reset()
    executor = UniversalExecutor(retries=1, backoff_factor=0.01)

    attempts = 0

    async def failing_task():
        """TODO: Add docstring."""
        nonlocal attempts
        attempts += 1
        raise ValueError("Async Error")

    # Use a regular function returning a coroutine, to match Callable[[], Awaitable[T]]
    def task_factory():
        """TODO: Add docstring."""
        return failing_task()

    with pytest.raises(ValueError, match="Async Error"):
        await executor.execute_async(task_factory)
    assert attempts == 2
