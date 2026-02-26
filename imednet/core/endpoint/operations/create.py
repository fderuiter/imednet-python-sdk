"""
Operation logic for creating resources.

This module defines the CreateOperation class, which encapsulates the execution
logic for synchronous and asynchronous create operations (POST).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Generic, Optional, TypeVar

from imednet.core.endpoint.protocols import CreateEndpointProtocol
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol

T_RESP = TypeVar("T_RESP")


class CreateOperation(Generic[T_RESP]):
    """
    Encapsulates execution logic for create operations.

    Handles construction of request arguments, execution of POST requests,
    and processing of responses.
    """

    def __init__(self, endpoint: CreateEndpointProtocol[T_RESP]) -> None:
        self.endpoint = endpoint

    def execute_sync(
        self,
        client: RequestorProtocol,
        path: str,
        *,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        parse_func: Optional[Callable[[Any], T_RESP]] = None,
    ) -> T_RESP:
        """Execute synchronous create request."""
        kwargs = self.endpoint._prepare_kwargs(json=json, data=data, headers=headers)
        response = client.post(path, **kwargs)
        return self.endpoint._process_response(response, parse_func)

    async def execute_async(
        self,
        client: AsyncRequestorProtocol,
        path: str,
        *,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        parse_func: Optional[Callable[[Any], T_RESP]] = None,
    ) -> T_RESP:
        """Execute asynchronous create request."""
        kwargs = self.endpoint._prepare_kwargs(json=json, data=data, headers=headers)
        response = await client.post(path, **kwargs)
        return self.endpoint._process_response(response, parse_func)
