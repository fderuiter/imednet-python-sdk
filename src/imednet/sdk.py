"""
Public entry-point for the iMednet SDK.

This module provides the ImednetSDK class which:
- Manages configuration and authentication
- Exposes all endpoint functionality through a unified interface
- Provides context management for proper resource cleanup
"""

from __future__ import annotations

from contextlib import contextmanager
from importlib import import_module
from typing import TYPE_CHECKING, Any, Iterator, Optional

from .config import Config, load_config
from .core.context import Context, reset_study_context, set_study_context
from .core.factory import ClientFactory
from .core.retry import RetryPolicy
from .endpoints.registry import ENDPOINT_REGISTRY
from .sdk_convenience import SDKConvenienceMixin

if TYPE_CHECKING:
    from .core.async_client import AsyncClient
    from .core.client import Client
    from .endpoints.codings import CodingsEndpoint
    from .endpoints.forms import FormsEndpoint
    from .endpoints.intervals import IntervalsEndpoint
    from .endpoints.jobs import JobsEndpoint
    from .endpoints.queries import QueriesEndpoint
    from .endpoints.record_revisions import RecordRevisionsEndpoint
    from .endpoints.records import RecordsEndpoint
    from .endpoints.sites import SitesEndpoint
    from .endpoints.studies import StudiesEndpoint
    from .endpoints.subjects import SubjectsEndpoint
    from .endpoints.users import UsersEndpoint
    from .endpoints.variables import VariablesEndpoint
    from .endpoints.visits import VisitsEndpoint


class ImednetSDK(SDKConvenienceMixin):
    """
    Public entry-point for library users.

    Provides access to all iMednet API endpoints and maintains configuration.
    """

    codings: CodingsEndpoint
    forms: FormsEndpoint
    intervals: IntervalsEndpoint
    jobs: JobsEndpoint
    queries: QueriesEndpoint
    record_revisions: RecordRevisionsEndpoint
    records: RecordsEndpoint
    sites: SitesEndpoint
    studies: StudiesEndpoint
    subjects: SubjectsEndpoint
    users: UsersEndpoint
    variables: VariablesEndpoint
    visits: VisitsEndpoint
    config: Config

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
        retry_policy: RetryPolicy | None = None,
        enable_async: bool = False,
        client: Optional[Client] = None,
        async_client: Optional[AsyncClient] = None,
    ) -> None:
        """Initialize the SDK with credentials and configuration."""

        config = load_config(api_key=api_key, security_key=security_key, base_url=base_url)

        self.config = config
        self._api_key = config.api_key
        self._security_key = config.security_key
        self._base_url = config.base_url

        endpoint_context = Context()

        if client:
            self._client = client
        else:
            self._client = ClientFactory.create_client(
                config=config,
                timeout=timeout,
                retries=retries,
                backoff_factor=backoff_factor,
                retry_policy=retry_policy,
            )

        if async_client:
            self._async_client: Optional[AsyncClient] = async_client
        elif enable_async:
            self._async_client = ClientFactory.create_async_client(
                config=config,
                timeout=timeout,
                retries=retries,
                backoff_factor=backoff_factor,
                retry_policy=retry_policy,
            )
        else:
            self._async_client = None

        self._init_endpoints(endpoint_context)
        self.workflows = self._init_workflows()

    @property
    def retry_policy(self) -> RetryPolicy:
        return self._client.retry_policy

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        self._client.retry_policy = policy
        if self._async_client is not None:
            self._async_client.retry_policy = policy

    def _init_endpoints(self, ctx: Context) -> None:
        """Instantiate endpoint clients."""
        for attr, endpoint_cls in ENDPOINT_REGISTRY.items():
            setattr(self, attr, endpoint_cls(self._client, ctx, self._async_client))

    def _init_workflows(self) -> Any:
        """Instantiate workflow namespace when optional workflows plugin is available."""

        def _init_local_workflows() -> Any:
            try:
                from .workflows.namespace import Workflows

                return Workflows(self)
            except (ImportError, ModuleNotFoundError):

                class _MissingWorkflows:
                    def __getattr__(self, name: str) -> Any:
                        raise ImportError(
                            (
                                f"Workflow '{name}' requires the optional "
                                "'imednet-workflows' package. "
                                "Install with `pip install imednet-workflows`."
                            )
                        )

                return _MissingWorkflows()

        try:
            workflows_module = import_module("imednet_workflows.namespace")
        except ModuleNotFoundError as error:
            if error.name and error.name.startswith("imednet_workflows"):
                return _init_local_workflows()
            raise

        workflows_cls = getattr(workflows_module, "Workflows", None)
        if workflows_cls is None:
            raise ImportError(
                "The optional imednet-workflows package is installed, but its "
                "'imednet_workflows.namespace' module does not export 'Workflows'."
            )
        try:
            return workflows_cls(self)
        except AttributeError as error:
            raise ImportError(
                "Failed to instantiate Workflows from imednet_workflows.namespace."
            ) from error

    def __enter__(self) -> ImednetSDK:
        """Support for context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup resources when exiting context."""
        self.close()

    async def __aenter__(self) -> "ImednetSDK":
        """Prevent accidental ``async with`` usage on the synchronous client."""
        raise TypeError(
            "ImednetSDK is a synchronous client. "
            "Use 'with ImednetSDK(...):' instead of 'async with'. "
            "If you require async execution, use AsyncImednetSDK."
        )

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Prevent direct or indirect invocation of the async exit on the sync client."""
        raise TypeError(
            "ImednetSDK is a synchronous client. "
            "Use 'with ImednetSDK(...):' instead of 'async with'. "
            "If you require async execution, use AsyncImednetSDK."
        )

    def close(self) -> None:
        """Close the synchronous client connection and free resources.

        Raises:
            RuntimeError: If an asynchronous client is active. Call
                ``await sdk.aclose()`` instead, or use
                ``async with AsyncImednetSDK(...)`` to manage the lifecycle.
        """
        if self._async_client is not None:
            raise RuntimeError(
                "This SDK instance has an active asynchronous client. "
                "Call `await sdk.aclose()` to properly clean up async resources, "
                "or use `async with AsyncImednetSDK(...)` to manage the lifecycle."
            )
        self._client.close()

    async def aclose(self) -> None:
        if self._async_client is not None:
            await self._async_client.aclose()
        self._client.close()

    @contextmanager
    def study_context(self, study_key: str) -> Iterator[ImednetSDK]:
        """Set a temporary default study key for the current thread/task context."""
        token = set_study_context(study_key)
        try:
            yield self
        finally:
            reset_study_context(token)


class AsyncImednetSDK(ImednetSDK):
    """Async variant of :class:`ImednetSDK` using the async HTTP client.

    Always use this class with ``async with`` or call ``await sdk.aclose()``
    explicitly when done. Using the synchronous context manager (``with``) or
    synchronous ``close()`` on this class will raise a :exc:`TypeError`.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - thin wrapper
        kwargs["enable_async"] = True
        super().__init__(*args, **kwargs)

    def close(self) -> None:
        """Raises :exc:`TypeError` — use ``await sdk.aclose()`` instead."""
        raise TypeError(
            "AsyncImednetSDK does not support the synchronous close() method. "
            "Use `await sdk.aclose()` or `async with AsyncImednetSDK(...)` instead."
        )

    def __enter__(self) -> "AsyncImednetSDK":
        raise TypeError(
            "AsyncImednetSDK does not support the synchronous context manager protocol. "
            "Use `async with AsyncImednetSDK(...)` instead."
        )

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        raise TypeError(
            "AsyncImednetSDK does not support the synchronous context manager protocol. "
            "Use `async with AsyncImednetSDK(...)` instead."
        )

    async def __aenter__(self) -> "AsyncImednetSDK":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()


__all__ = ["ImednetSDK", "AsyncImednetSDK"]
