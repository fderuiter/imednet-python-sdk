from typing import Any, Awaitable, Protocol, TypeVar, runtime_checkable

T = TypeVar("T", covariant=True)


@runtime_checkable
class OperationProtocol(Protocol[T]):
    """Protocol for synchronous operations."""

    def execute(self, *args: Any, **kwargs: Any) -> T: ...


@runtime_checkable
class AsyncOperationProtocol(Protocol[T]):
    """Protocol for asynchronous operations."""

    def execute(self, *args: Any, **kwargs: Any) -> Awaitable[T]: ...
