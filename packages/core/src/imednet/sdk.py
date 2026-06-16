"""
Public entry-point for the iMednet SDK.

This module provides the ImednetSDK class which:
- Manages configuration and authentication
- Exposes all endpoint functionality through a unified interface
- Provides context management for proper resource cleanup
"""

from __future__ import annotations

from contextlib import contextmanager
from importlib.metadata import EntryPoint, entry_points
from typing import TYPE_CHECKING, Any, Iterator, Optional, cast

from .config import Config, load_config
from .core.context import study_context
from .core.factory import ClientFactory
from .core.retry import RetryPolicy
from .endpoints.registry import ASYNC_ENDPOINT_REGISTRY, ENDPOINT_REGISTRY
from .errors import PluginLoadError
from .plugins import (
    PluginProtocol,
    SinksNamespaceProtocol,
    SinksPluginProtocol,
    WorkflowsNamespaceProtocol,
)
from .sdk_convenience import AsyncSDKConvenienceMixin, SyncSDKConvenienceMixin

if TYPE_CHECKING:
    from .core.async_client import AsyncClient
    from .core.client import Client
    from .endpoints.codings import AsyncCodingsEndpoint, CodingsEndpoint
    from .endpoints.forms import AsyncFormsEndpoint, FormsEndpoint
    from .endpoints.intervals import AsyncIntervalsEndpoint, IntervalsEndpoint
    from .endpoints.jobs import AsyncJobsEndpoint, JobsEndpoint
    from .endpoints.queries import AsyncQueriesEndpoint, QueriesEndpoint
    from .endpoints.record_revisions import AsyncRecordRevisionsEndpoint, RecordRevisionsEndpoint
    from .endpoints.records import AsyncRecordsEndpoint, RecordsEndpoint
    from .endpoints.sites import AsyncSitesEndpoint, SitesEndpoint
    from .endpoints.studies import AsyncStudiesEndpoint, StudiesEndpoint
    from .endpoints.subjects import AsyncSubjectsEndpoint, SubjectsEndpoint
    from .endpoints.users import AsyncUsersEndpoint, UsersEndpoint
    from .endpoints.variables import AsyncVariablesEndpoint, VariablesEndpoint
    from .endpoints.visits import AsyncVisitsEndpoint, VisitsEndpoint


class WorkflowPluginProtocol(PluginProtocol):
    """Alias kept for backwards compatibility; use :class:`~imednet.plugins.PluginProtocol` instead."""  # noqa: E501


class _BaseSDK:
    config: Config

    def _get_plugin_entry_point(self, name: str) -> EntryPoint | None:
        """Return the configured plugin entry point."""
        plugin_entry_points = list(entry_points(group="imednet.plugins", name=name))

        if not plugin_entry_points:
            return None
        if len(plugin_entry_points) > 1:
            discovered_plugins = ", ".join(
                sorted(entry_point.value for entry_point in plugin_entry_points)
            )
            raise PluginLoadError(
                f"Multiple '{name}' plugins were found in the 'imednet.plugins' entry-point "
                f"group ({discovered_plugins}). Please keep only one {name} plugin installed."
            )
        return plugin_entry_points[0]

    def _get_workflow_entry_point(self) -> EntryPoint | None:
        return self._get_plugin_entry_point("workflows")

    def _init_workflows(self) -> Optional[WorkflowsNamespaceProtocol]:
        """Instantiate workflow namespace when optional workflows plugin is available."""

        workflows_entry_point = self._get_workflow_entry_point()
        if workflows_entry_point is None:
            class _MissingWorkflows:
                def __getattr__(self, name: str) -> Any:
                    raise ImportError("This feature requires the optional 'imednet-workflows' package.")
            return _MissingWorkflows()  # type: ignore

        try:
            workflows_plugin = workflows_entry_point.load()
        except (AttributeError, ImportError, ModuleNotFoundError) as error:
            raise PluginLoadError(
                f"Failed to load workflows plugin from entry point '{workflows_entry_point.value}'."
            ) from error

        if not callable(workflows_plugin):
            raise PluginLoadError(
                "The workflows plugin entry point "
                f"'{workflows_entry_point.value}' must be a callable that accepts an SDK "
                f"instance; got {type(workflows_plugin).__name__}."
            )

        try:
            workflows_factory = cast(PluginProtocol, workflows_plugin)
            return workflows_factory(cast(Any, self))
        except TypeError as error:
            raise PluginLoadError(
                "Failed to instantiate workflows from the discovered plugin entry point."
            ) from error

    def _init_sinks(self) -> Optional[SinksNamespaceProtocol]:
        """Instantiate sinks namespace when optional sinks plugin is available."""

        sinks_entry_point = self._get_plugin_entry_point("sinks")
        if sinks_entry_point is None:
            return None

        try:
            sinks_plugin = sinks_entry_point.load()
        except (AttributeError, ImportError, ModuleNotFoundError) as error:
            raise PluginLoadError(
                f"Failed to load sinks plugin from entry point '{sinks_entry_point.value}'."
            ) from error

        if not callable(sinks_plugin):
            raise PluginLoadError(
                "The sinks plugin entry point "
                f"'{sinks_entry_point.value}' must be a callable that accepts an SDK "
                f"instance; got {type(sinks_plugin).__name__}."
            )

        try:
            sinks_factory = cast(SinksPluginProtocol, sinks_plugin)
            return sinks_factory(cast(Any, self))
        except TypeError as error:
            raise PluginLoadError(
                "Failed to instantiate sinks from the discovered plugin entry point."
            ) from error

    @contextmanager
    def study_context(self, study_key: str) -> Iterator[Any]:
        """Set a temporary default study key for the current thread/task context."""
        with study_context(study_key):
            yield self


class ImednetSDK(_BaseSDK, SyncSDKConvenienceMixin):
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
    workflows: Optional[WorkflowsNamespaceProtocol]
    sinks: Optional[SinksNamespaceProtocol]
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
        client: Optional[Client] = None,
    ) -> None:
        """Initialize the SDK with credentials and configuration."""

        config = load_config(api_key=api_key, security_key=security_key, base_url=base_url)

        self.config = config
        self._api_key = config.api_key
        self._security_key = config.security_key
        self._base_url = config.base_url

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

        self._init_endpoints()
        self.workflows = self._init_workflows()
        self.sinks = self._init_sinks()

    @property
    def auth(self) -> Any:
        return getattr(self._client, "auth", None)

    @property
    def retry_policy(self) -> RetryPolicy:
        return self._client.retry_policy

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        self._client.retry_policy = policy

    def _init_endpoints(self) -> None:
        """Instantiate endpoint clients."""
        for attr, endpoint_cls in ENDPOINT_REGISTRY.items():
            setattr(self, attr, endpoint_cls(self._client))

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
        """Close the synchronous client connection and free resources."""
        self._client.close()

    async def aclose(self) -> None:
        raise TypeError(
            "ImednetSDK is a synchronous client. "
            "Use `sdk.close()` or `with ImednetSDK(...)` instead. "
            "If you require async execution, use AsyncImednetSDK."
        )


class AsyncImednetSDK(_BaseSDK, AsyncSDKConvenienceMixin):
    """Async variant of :class:`ImednetSDK` using the async HTTP client.

    Always use this class with ``async with`` or call ``await sdk.aclose()``
    explicitly when done. Using the synchronous context manager (``with``) or
    synchronous ``close()`` on this class will raise a :exc:`TypeError`.
    """

    codings: AsyncCodingsEndpoint
    forms: AsyncFormsEndpoint
    intervals: AsyncIntervalsEndpoint
    jobs: AsyncJobsEndpoint
    queries: AsyncQueriesEndpoint
    record_revisions: AsyncRecordRevisionsEndpoint
    records: AsyncRecordsEndpoint
    sites: AsyncSitesEndpoint
    studies: AsyncStudiesEndpoint
    subjects: AsyncSubjectsEndpoint
    users: AsyncUsersEndpoint
    variables: AsyncVariablesEndpoint
    visits: AsyncVisitsEndpoint
    workflows: Optional[WorkflowsNamespaceProtocol]
    sinks: Optional[SinksNamespaceProtocol]

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
        retry_policy: RetryPolicy | None = None,
        async_client: Optional[AsyncClient] = None,
    ) -> None:
        config = load_config(api_key=api_key, security_key=security_key, base_url=base_url)
        self.config = config
        self._api_key = config.api_key
        self._security_key = config.security_key
        self._base_url = config.base_url

        self._async_client = async_client or ClientFactory.create_async_client(
            config=config,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            retry_policy=retry_policy,
        )

        self._init_endpoints()
        self.workflows = self._init_workflows()
        self.sinks = self._init_sinks()

    @property
    def auth(self) -> Any:
        return getattr(self._async_client, "auth", None)

    @property
    def retry_policy(self) -> RetryPolicy:
        return self._async_client.retry_policy

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        self._async_client.retry_policy = policy

    def _init_endpoints(self) -> None:
        for attr, endpoint_cls in ASYNC_ENDPOINT_REGISTRY.items():
            setattr(self, attr, endpoint_cls(self._async_client))  # type: ignore[arg-type]

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

    async def aclose(self) -> None:
        await self._async_client.aclose()


__all__ = ["ImednetSDK", "AsyncImednetSDK"]
