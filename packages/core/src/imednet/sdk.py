"""Public entry-point for the iMednet SDK.

This module provides the ImednetSDK class which:
- Manages configuration and authentication
- Exposes all endpoint functionality through a unified interface
- Provides context management for proper resource cleanup
"""

from __future__ import annotations

from contextlib import contextmanager
from importlib.metadata import EntryPoint, entry_points
from typing import TYPE_CHECKING, Any, Iterator, Optional, Union, cast

from .config import Config, load_config
from .core.context import study_context
from .core.factory import ClientFactory
from .core.retry import RetryPolicy
from .errors import PluginLoadError
from .plugins import (
    PluginProtocol,
    SinksNamespaceProtocol,
    SinksPluginProtocol,
    WorkflowsNamespaceProtocol,
)
from .sdk_convenience import AsyncSDKConvenienceMixin, SyncSDKConvenienceMixin
from .endpoints.registry import ENDPOINT_REGISTRY, ASYNC_ENDPOINT_REGISTRY

if TYPE_CHECKING:
    from .core.async_client import AsyncClient
    from .core.client import Client
    from .spi.facade import AsyncImednetFacade, ImednetFacade


class WorkflowPluginProtocol(PluginProtocol):
    """Alias kept for backwards compatibility; use :class:`~imednet.plugins.PluginProtocol` instead."""  # noqa: E501


class _BaseSDK:
    """Base class for iMednet SDK variants.

    Provides shared logic for configuration management, plugin discovery,
    and workflow/sink initialization.
    """

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
        """Return the configured workflow plugin entry point."""
        return self._get_plugin_entry_point("workflows")

    def _init_workflows(self) -> Optional[WorkflowsNamespaceProtocol]:
        """Instantiate workflow namespace when optional workflows plugin is available."""
        workflows_entry_point = self._get_workflow_entry_point()
        if workflows_entry_point is None:

            class _MissingWorkflows:
                """Proxy for missing workflows plugin.

                Raises ImportError when any workflow attribute is accessed.
                """

                def __getattr__(self, name: str) -> Any:
                    """Raise ImportError indicating the missing optional package."""
                    raise ImportError(
                        "This feature requires the optional 'imednet-workflows' package."
                    )

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
            return workflows_factory(cast(Union["ImednetFacade", "AsyncImednetFacade"], self))
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
    """Public entry-point for library users.

    Provides access to all iMednet API endpoints and maintains configuration.
    """

    workflows: Optional[WorkflowsNamespaceProtocol]
    sinks: Optional[SinksNamespaceProtocol]
    config: Config

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        strict_mode: Optional[bool] = None,
        retries: int = 3,
        backoff_factor: float = 1.0,
        retry_policy: RetryPolicy | None = None,
        client: Optional[Client] = None,
    ) -> None:
        """Initialize the SDK with credentials and configuration."""
        config = load_config(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
            timeout=timeout,
            strict_mode=strict_mode,
        )

        self.config = config
        self._api_key = config.api_key
        self._security_key = config.security_key
        self._base_url = config.base_url

        if client:
            self._client = client
        else:
            self._client = ClientFactory.create_client(
                config=config,
                timeout=config.timeout,
                retries=retries,
                backoff_factor=backoff_factor,
                retry_policy=retry_policy,
            )

        self._init_endpoints()
        self.workflows = self._init_workflows()
        self.sinks = self._init_sinks()

    @property
    def auth(self) -> Any:
        """Return the authentication provider used by the client."""
        return getattr(self._client, "auth", None)

    @property
    def retry_policy(self) -> RetryPolicy:
        """Return the current retry policy."""
        return self._client.retry_policy

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        """Set a new retry policy for the client."""
        self._client.retry_policy = policy

    def __getattr__(self, name: str) -> Any:
        return super().__getattribute__(name)

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
        """Asynchronous close is not supported on the synchronous SDK."""
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

    workflows: Optional[WorkflowsNamespaceProtocol]
    sinks: Optional[SinksNamespaceProtocol]

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        strict_mode: Optional[bool] = None,
        retries: int = 3,
        backoff_factor: float = 1.0,
        retry_policy: RetryPolicy | None = None,
        async_client: Optional[AsyncClient] = None,
    ) -> None:
        """Initialize the asynchronous SDK.

        Args:
            api_key: iMednet API key.
            security_key: iMednet security key.
            base_url: Base URL for the iMednet API.
            timeout: Default request timeout in seconds.
            strict_mode: Toggle strict mode for data validation.
            retries: Number of retry attempts.
            backoff_factor: Exponential backoff factor.
            retry_policy: Custom retry policy.
            async_client: Pre-configured async client instance.
        """
        config = load_config(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
            timeout=timeout,
            strict_mode=strict_mode,
        )
        self.config = config
        self._api_key = config.api_key
        self._security_key = config.security_key
        self._base_url = config.base_url

        self._async_client = async_client or ClientFactory.create_async_client(
            config=config,
            timeout=config.timeout,
            retries=retries,
            backoff_factor=backoff_factor,
            retry_policy=retry_policy,
        )

        self._init_endpoints()
        self.workflows = self._init_workflows()
        self.sinks = self._init_sinks()

    @property
    def auth(self) -> Any:
        """Return the authentication provider used by the async client."""
        return getattr(self._async_client, "auth", None)

    @property
    def retry_policy(self) -> RetryPolicy:
        """Return the current retry policy of the async client."""
        return self._async_client.retry_policy

    @retry_policy.setter
    def retry_policy(self, policy: RetryPolicy) -> None:
        """Set a new retry policy for the async client."""
        self._async_client.retry_policy = policy

    def __getattr__(self, name: str) -> Any:
        return super().__getattribute__(name)

    def _init_endpoints(self) -> None:
        """Initialize all asynchronous endpoint instances."""
        for attr, endpoint_cls in ASYNC_ENDPOINT_REGISTRY.items():
            setattr(self, attr, endpoint_cls(self._async_client))  # type: ignore[arg-type]

    def close(self) -> None:
        """Raises :exc:`TypeError` — use ``await sdk.aclose()`` instead."""
        raise TypeError(
            "AsyncImednetSDK does not support the synchronous close() method. "
            "Use `await sdk.aclose()` or `async with AsyncImednetSDK(...)` instead."
        )

    def __enter__(self) -> "AsyncImednetSDK":
        """Synchronous context manager is not supported."""
        raise TypeError(
            "AsyncImednetSDK does not support the synchronous context manager protocol. "
            "Use `async with AsyncImednetSDK(...)` instead."
        )

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Synchronous context manager is not supported."""
        raise TypeError(
            "AsyncImednetSDK does not support the synchronous context manager protocol. "
            "Use `async with AsyncImednetSDK(...)` instead."
        )

    async def __aenter__(self) -> "AsyncImednetSDK":
        """Enter the asynchronous context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the asynchronous context manager and close the client."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying asynchronous client and free resources."""
        await self._async_client.aclose()


__all__ = ["ImednetSDK", "AsyncImednetSDK"]
