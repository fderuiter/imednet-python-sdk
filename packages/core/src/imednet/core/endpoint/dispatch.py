"""Dynamic dispatch descriptors for unified sync/async endpoint execution."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Coroutine, Iterator
from imednet.core.endpoint.operations.list import ListOperation
from imednet.core.endpoint.operations.filter_get import FilterGetOperation
from typing import Any, Generic, TypeVar, overload
from typing_extensions import Concatenate, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")

class SyncEndpointContext:
    """Marker class for synchronous endpoints."""

class AsyncEndpointContext:
    """Marker class for asynchronous endpoints."""

class SyncClientContext:
    """Marker class for synchronous SDK client."""

class AsyncClientContext:
    """Marker class for asynchronous SDK client."""

class Operation(Generic[T]):
    """Protocol for an Operation that can be executed both ways."""
    def execute_sync(self, client: Any, parse_func: Any = None) -> T: raise NotImplementedError
    async def execute_async(self, client: Any, parse_func: Any = None) -> T: raise NotImplementedError

class execute_operation(Generic[P, T]):
    """Descriptor that dispatches an operation-returning method to sync/async execution."""

    def __init__(self, func: Callable[Concatenate[Any, P], Operation[T]]):
        self.func = func

    @overload
    def __get__(self, instance: SyncEndpointContext, owner: Any) -> Callable[P, T]: ...

    @overload
    def __get__(self, instance: AsyncEndpointContext, owner: Any) -> Callable[P, Coroutine[Any, Any, T]]: ...

    @overload
    def __get__(self, instance: None, owner: Any) -> execute_operation[P, T]: ...

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self

        is_async = isinstance(instance, AsyncEndpointContext)
        func = self.func

        if is_async:
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                op = func(instance, *args, **kwargs)
                return await op.execute_async(instance._require_async_client()) # type: ignore
            return async_wrapper
        else:
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                op = func(instance, *args, **kwargs)
                return op.execute_sync(instance._require_sync_client()) # type: ignore
            return sync_wrapper

class execute_list(Generic[P, T]):
    """Descriptor that dispatches a list operation."""

    def __init__(self, func: Callable[Concatenate[Any, P], ListOperation[T]]):
        self.func = func

    @overload
    def __get__(self, instance: SyncEndpointContext, owner: Any) -> Callable[P, Iterator[T]]: ...

    @overload
    def __get__(self, instance: AsyncEndpointContext, owner: Any) -> Callable[P, AsyncIterator[T]]: ...

    @overload
    def __get__(self, instance: None, owner: Any) -> execute_list[P, T]: ...

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self

        is_async = isinstance(instance, AsyncEndpointContext)
        func = self.func

        if is_async:
            def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> AsyncIterator[T]:
                op = func(instance, *args, **kwargs)
                return op.execute_async(instance._require_async_client(), instance.ASYNC_PAGINATOR_CLS) # type: ignore
            return async_wrapper
        else:
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Iterator[T]:
                op = func(instance, *args, **kwargs)
                return op.execute_sync(instance._require_sync_client(), instance.PAGINATOR_CLS) # type: ignore
            return sync_wrapper

class execute_get(Generic[P, T]):
    """Descriptor that dispatches a get operation."""

    def __init__(self, func: Callable[Concatenate[Any, P], FilterGetOperation[T]]):
        self.func = func

    @overload
    def __get__(self, instance: SyncEndpointContext, owner: Any) -> Callable[P, T]: ...

    @overload
    def __get__(self, instance: AsyncEndpointContext, owner: Any) -> Callable[P, Coroutine[Any, Any, T]]: ...

    @overload
    def __get__(self, instance: None, owner: Any) -> execute_get[P, T]: ...

    def __get__(self, instance: Any, owner: Any) -> Any:
        if instance is None:
            return self

        is_async = isinstance(instance, AsyncEndpointContext)
        func = self.func

        if is_async:
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                op = func(instance, *args, **kwargs)
                return await op.execute_async(instance._require_async_client(), instance.ASYNC_PAGINATOR_CLS) # type: ignore
            return async_wrapper
        else:
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                op = func(instance, *args, **kwargs)
                return op.execute_sync(instance._require_sync_client(), instance.PAGINATOR_CLS) # type: ignore
            return sync_wrapper
