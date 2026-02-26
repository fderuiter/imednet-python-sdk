from __future__ import annotations

from typing import Any, Callable, Dict, Generic, Optional, TypeVar, cast

import httpx

from imednet.core.endpoint.operations.create import CreateOperation
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

T_RESP = TypeVar("T_RESP")


class CreateEndpointMixin(Generic[T_RESP]):
    """Mixin implementing creation logic."""

    CREATE_OPERATION_CLS: type[CreateOperation[T_RESP]] = CreateOperation

    def _prepare_kwargs(
        self,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Prepare keyword arguments for the request.

        Filters out None values to preserve default behavior.
        """
        kwargs: Dict[str, Any] = {}
        if json is not None:
            kwargs["json"] = json
        if data is not None:
            kwargs["data"] = data
        if headers is not None:
            kwargs["headers"] = headers
        return kwargs

    def _process_response(
        self,
        response: httpx.Response,
        parse_func: Optional[Callable[[Any], T_RESP]] = None,
    ) -> T_RESP:
        """
        Process the API response and parse the result.

        Args:
            response: The HTTP response object.
            parse_func: Optional function to parse the JSON payload.

        Returns:
            The parsed response object.
        """
        payload = response.json()
        if parse_func:
            return parse_func(payload)
        return cast(T_RESP, payload)

    def _create_sync(
        self,
        client: RequestorProtocol,
        path: str,
        *,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        parse_func: Optional[Callable[[Any], T_RESP]] = None,
    ) -> T_RESP:
        """
        Execute a synchronous creation request (POST).
        """
        op = self.CREATE_OPERATION_CLS(self)
        return op.execute_sync(
            client,
            path,
            json=json,
            data=data,
            headers=headers,
            parse_func=parse_func,
        )

    async def _create_async(
        self,
        client: AsyncRequestorProtocol,
        path: str,
        *,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        parse_func: Optional[Callable[[Any], T_RESP]] = None,
    ) -> T_RESP:
        """
        Execute an asynchronous creation request (POST).
        """
        op = self.CREATE_OPERATION_CLS(self)
        return await op.execute_async(
            client,
            path,
            json=json,
            data=data,
            headers=headers,
            parse_func=parse_func,
        )
