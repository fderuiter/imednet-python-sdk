import inspect
from typing import Any, Callable, Coroutine, TypeVar, Union

R = TypeVar("R")  # Response Type
T = TypeVar("T")  # Result Type


def call_sync_or_async(
    request_func: Callable[..., Union[R, Coroutine[Any, Any, R]]],
    process_func: Callable[[R], T],
    *args: Any,
    **kwargs: Any,
) -> Union[T, Coroutine[Any, Any, T]]:
    """
    Dispatches a request function (sync or async) and processes the result.

    If ``request_func`` is an async function (coroutine function), returns an
    awaitable that awaits the request and then calls ``process_func`` on the
    result.

    If ``request_func`` is a sync function, calls it immediately and returns
    the result of ``process_func``.

    Args:
        request_func: The function to make the request (e.g. client.get).
        process_func: A function to process the response (e.g. parse JSON).
        *args: Arguments to pass to request_func.
        **kwargs: Keyword arguments to pass to request_func.

    Returns:
        The processed result (T) or a coroutine resolving to it.
    """
    if inspect.iscoroutinefunction(request_func):

        async def _wrapper() -> T:
            response = await request_func(*args, **kwargs)
            return process_func(response)

        return _wrapper()

    response = request_func(*args, **kwargs)
    return process_func(response)
