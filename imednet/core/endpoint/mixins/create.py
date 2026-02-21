from __future__ import annotations

from typing import Any, Callable, Dict, Generic, Optional, TypeVar, cast

import httpx
from pydantic import BaseModel

from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

T_RESP = TypeVar("T_RESP")


class CreateEndpointMixin(Generic[T_RESP]):
    """Mixin implementing creation logic."""

    def _prepare_kwargs(
        self,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Prepare keyword arguments for the request.

        Filters out None values to preserve default behavior.
        Also serializes Pydantic models in json payload.
        """
        kwargs: Dict[str, Any] = {}
        if json is not None:
            if isinstance(json, list):
                json = [
                    (item.model_dump(by_alias=True) if isinstance(item, BaseModel) else item)
                    for item in json
                ]
            elif isinstance(json, BaseModel):
                json = json.model_dump(by_alias=True)
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
        kwargs = self._prepare_kwargs(json=json, data=data, headers=headers)
        response = client.post(path, **kwargs)
        return self._process_response(response, parse_func)

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
        kwargs = self._prepare_kwargs(json=json, data=data, headers=headers)
        response = await client.post(path, **kwargs)
        return self._process_response(response, parse_func)
