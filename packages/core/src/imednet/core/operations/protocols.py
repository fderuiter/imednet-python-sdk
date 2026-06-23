"""Protocols defining the interface for operations within the iMednet SDK."""

from typing import Any, Awaitable, Protocol, TypeVar, runtime_checkable

T = TypeVar("T", covariant=True)


@runtime_checkable
class OperationProtocol(Protocol[T]):
    """Protocol for synchronous operations."""

    def execute(self, *args: Any, **kwargs: Any) -> T:
        """Execute the operation synchronously.

        Args:
            *args: Variable positional arguments for the operation.
            **kwargs: Variable keyword arguments for the operation.

        Returns:
            T: The result of the operation.
        """
        ...


@runtime_checkable
class AsyncOperationProtocol(Protocol[T]):
    """Protocol for asynchronous operations."""

    def execute(self, *args: Any, **kwargs: Any) -> Awaitable[T]:
        """Execute the operation asynchronously.

        Args:
            *args: Variable positional arguments for the operation.
            **kwargs: Variable keyword arguments for the operation.

        Returns:
            Awaitable[T]: An awaitable that resolves to the result of the operation.
        """
        ...
