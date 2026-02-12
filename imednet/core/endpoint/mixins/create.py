from __future__ import annotations

import inspect
from typing import Any, Awaitable, Callable, Dict, Generic, Optional, TypeVar, cast

from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

T_RESP = TypeVar("T_RESP")


class CreateEndpointMixin(Generic[T_RESP]):
    """Mixin implementing creation logic."""

    def _create_impl(
        self,
        client: RequestorProtocol | AsyncRequestorProtocol,
        path: str,
        *,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        parse_func: Optional[Callable[[Any], T_RESP]] = None,
    ) -> T_RESP | Awaitable[T_RESP]:
        """
        Execute a creation request (POST).

        Handles both sync and async execution based on the client type.
        """

        def process_response(response: Any) -> T_RESP:
            payload = response.json()
            if parse_func:
                return parse_func(payload)
            return cast(T_RESP, payload)

        # Prepare kwargs to filter out None values to preserve default behavior
        kwargs: Dict[str, Any] = {}
        if json is not None:
            kwargs["json"] = json
        if data is not None:
            kwargs["data"] = data
        if headers is not None:
            kwargs["headers"] = headers

        if inspect.iscoroutinefunction(client.post):

            async def _await() -> T_RESP:
                response = await client.post(path, **kwargs)  # type: ignore
                return process_response(response)

            return _await()

        response = client.post(path, **kwargs)  # type: ignore
        return process_response(response)
