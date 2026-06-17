"""
Convenience mixins for the iMedNet SDK.

These mixins contain high-level helper methods that delegate to specific endpoints.
They are architecturally linked to the core execution engine.
"""

from __future__ import annotations

from importlib import import_module
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Protocol,
    TypeVar,
    Union,
)

from imednet.models.codings import Coding
from imednet.models.forms import Form
from imednet.models.intervals import Interval
from imednet.models.jobs import Job, JobStatus
from imednet.models.queries import Query
from imednet.models.record_revisions import RecordRevision
from imednet.models.records import Record
from imednet.models.sites import Site
from imednet.models.studies import Study
from imednet.models.subjects import Subject
from imednet.models.users import User
from imednet.models.variables import Variable
from imednet.models.visits import Visit
from imednet.utils.typing import FilterValue, JsonDict

try:
    from opentelemetry import trace as _trace

    tracer: Any = _trace.get_tracer(__name__)
except Exception:
    tracer = None


def _trace_method(func: Callable[..., Any]) -> Callable[..., Any]:
    from functools import wraps

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if tracer:
            with tracer.start_as_current_span(func.__name__):
                return func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


def _async_trace_method(func: Callable[..., Any]) -> Callable[..., Any]:
    from functools import wraps

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if tracer:
            with tracer.start_as_current_span(func.__name__):
                return await func(*args, **kwargs)
        return await func(*args, **kwargs)

    return wrapper


if TYPE_CHECKING:
    from imednet.endpoints.codings import AsyncCodingsEndpoint, CodingsEndpoint
    from imednet.endpoints.forms import AsyncFormsEndpoint, FormsEndpoint
    from imednet.endpoints.intervals import AsyncIntervalsEndpoint, IntervalsEndpoint
    from imednet.endpoints.jobs import AsyncJobsEndpoint, JobsEndpoint
    from imednet.endpoints.queries import AsyncQueriesEndpoint, QueriesEndpoint
    from imednet.endpoints.record_revisions import (
        AsyncRecordRevisionsEndpoint,
        RecordRevisionsEndpoint,
    )
    from imednet.endpoints.records import AsyncRecordsEndpoint, RecordsEndpoint
    from imednet.endpoints.sites import AsyncSitesEndpoint, SitesEndpoint
    from imednet.endpoints.studies import AsyncStudiesEndpoint, StudiesEndpoint
    from imednet.endpoints.subjects import AsyncSubjectsEndpoint, SubjectsEndpoint
    from imednet.endpoints.users import AsyncUsersEndpoint, UsersEndpoint
    from imednet.endpoints.variables import AsyncVariablesEndpoint, VariablesEndpoint
    from imednet.endpoints.visits import AsyncVisitsEndpoint, VisitsEndpoint


def _workflow_poller(name: str) -> Any:
    try:
        module = import_module("imednet_workflows.job_poller")
    except ModuleNotFoundError as error:
        if error.name and error.name.startswith("imednet_workflows"):
            raise ImportError(
                "Job polling requires the optional 'imednet-workflows' package. "
                "Install with `pip install imednet-workflows`."
            ) from error
        raise
    return getattr(module, name)


def JobPoller(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _workflow_poller("JobPoller")(*args, **kwargs)


def AsyncJobPoller(*args: Any, **kwargs: Any) -> Any:  # noqa: N802
    return _workflow_poller("AsyncJobPoller")(*args, **kwargs)


T = TypeVar("T")


class _SyncListOperation(Generic[T]):
    def __init__(self, endpoint_name: str, name: str):
        self.endpoint_name = endpoint_name
        self.name = name

    def __get__(self, instance: Any, owner: Any) -> Callable[..., List[T]]:
        if instance is None:

            def unbound_wrapper(study_key: str | None = None, **filters: FilterValue) -> List[T]:
                raise NotImplementedError

            unbound_wrapper.__name__ = self.name
            unbound_wrapper.__qualname__ = f"{owner.__name__}.{self.name}"
            unbound_wrapper.__module__ = owner.__module__
            unbound_wrapper.__doc__ = f"List {self.endpoint_name}."
            return _trace_method(unbound_wrapper)
        endpoint = getattr(instance, self.endpoint_name)

        def wrapper(study_key: str | None = None, **filters: FilterValue) -> List[T]:
            _filters: Dict[str, Any] = dict(filters)
            if self.endpoint_name == "studies":
                return list(endpoint.list(**_filters))
            return list(endpoint.list(study_key, **_filters))

        wrapper.__name__ = self.name
        wrapper.__qualname__ = f"{instance.__class__.__name__}.{self.name}"
        wrapper.__module__ = instance.__class__.__module__
        wrapper.__doc__ = f"List {self.endpoint_name}."
        return _trace_method(wrapper)


class _AsyncListOperation(Generic[T]):
    def __init__(self, endpoint_name: str, name: str):
        self.endpoint_name = endpoint_name
        self.name = name

    def __get__(self, instance: Any, owner: Any) -> Callable[..., Awaitable[List[T]]]:
        if instance is None:

            async def unbound_wrapper(
                study_key: str | None = None, **filters: FilterValue
            ) -> List[T]:
                raise NotImplementedError

            unbound_wrapper.__name__ = self.name
            unbound_wrapper.__qualname__ = f"{owner.__name__}.{self.name}"
            unbound_wrapper.__module__ = owner.__module__
            unbound_wrapper.__doc__ = f"Asynchronously list {self.endpoint_name}."
            return _async_trace_method(unbound_wrapper)
        endpoint = getattr(instance, self.endpoint_name)

        async def wrapper(study_key: str | None = None, **filters: FilterValue) -> List[T]:
            _filters: Dict[str, Any] = dict(filters)
            if self.endpoint_name == "studies":
                res = endpoint.async_list(**_filters)
                return [item async for item in res] if hasattr(res, "__aiter__") else await res
            res = endpoint.async_list(study_key, **_filters)
            return [item async for item in res] if hasattr(res, "__aiter__") else await res

        wrapper.__name__ = self.name
        wrapper.__qualname__ = f"{instance.__class__.__name__}.{self.name}"
        wrapper.__module__ = instance.__class__.__module__
        wrapper.__doc__ = f"Asynchronously list {self.endpoint_name}."
        return _async_trace_method(wrapper)


class SyncSDKConvenienceMixin:
    """Synchronous SDK convenience methods."""

    if TYPE_CHECKING:
        jobs: JobsEndpoint
        records: RecordsEndpoint

    get_codings = _SyncListOperation[Coding]("codings", "get_codings")
    get_forms = _SyncListOperation[Form]("forms", "get_forms")
    get_intervals = _SyncListOperation[Interval]("intervals", "get_intervals")
    get_queries = _SyncListOperation[Query]("queries", "get_queries")
    get_record_revisions = _SyncListOperation[RecordRevision](
        "record_revisions", "get_record_revisions"
    )
    get_records = _SyncListOperation[Record]("records", "get_records")
    get_sites = _SyncListOperation[Site]("sites", "get_sites")
    get_studies = _SyncListOperation[Study]("studies", "get_studies")
    get_subjects = _SyncListOperation[Subject]("subjects", "get_subjects")
    get_users = _SyncListOperation[User]("users", "get_users")
    get_variables = _SyncListOperation[Variable]("variables", "get_variables")
    get_visits = _SyncListOperation[Visit]("visits", "get_visits")

    @_trace_method
    def get_job(self, study_key: str, batch_id: str) -> JobStatus:
        """Get job status."""
        return self.jobs.get(study_key, batch_id)

    @_trace_method
    def create_record(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Any = None,
    ) -> Job:
        """Create records in the specified study."""
        return self.records.create(
            study_key, records_data, email_notify=email_notify, schema=schema
        )

    @_trace_method
    def poll_job(
        self,
        study_key: str,
        batch_id: str,
        *,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        """Poll a job until it reaches a terminal state."""
        fetch_result = getattr(self, "_client", None) and getattr(
            getattr(self, "_client", None), "get", None
        )
        from typing import cast

        return cast(JobStatus, JobPoller(self.jobs.get).run(study_key, batch_id, interval, timeout))


class AsyncSDKConvenienceMixin:
    """Asynchronous SDK convenience methods."""

    if TYPE_CHECKING:
        import httpx

        jobs: AsyncJobsEndpoint
        records: AsyncRecordsEndpoint
        from imednet.core.async_client import AsyncClient

        _async_client: AsyncClient

    async_get_codings = _AsyncListOperation[Coding]("codings", "async_get_codings")
    async_get_forms = _AsyncListOperation[Form]("forms", "async_get_forms")
    async_get_intervals = _AsyncListOperation[Interval]("intervals", "async_get_intervals")
    async_get_queries = _AsyncListOperation[Query]("queries", "async_get_queries")
    async_get_record_revisions = _AsyncListOperation[RecordRevision](
        "record_revisions", "async_get_record_revisions"
    )
    async_get_records = _AsyncListOperation[Record]("records", "async_get_records")
    async_get_sites = _AsyncListOperation[Site]("sites", "async_get_sites")
    async_get_studies = _AsyncListOperation[Study]("studies", "async_get_studies")
    async_get_subjects = _AsyncListOperation[Subject]("subjects", "async_get_subjects")
    async_get_users = _AsyncListOperation[User]("users", "async_get_users")
    async_get_variables = _AsyncListOperation[Variable]("variables", "async_get_variables")
    async_get_visits = _AsyncListOperation[Visit]("visits", "async_get_visits")

    @_async_trace_method
    async def async_get_job(self, study_key: str, batch_id: str) -> JobStatus:
        """Asynchronously get job status."""
        return await self.jobs.async_get(study_key, batch_id)

    @_async_trace_method
    async def async_create_record(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Any = None,
    ) -> Job:
        """Asynchronously create records in the specified study."""
        return await self.records.async_create(
            study_key, records_data, email_notify=email_notify, schema=schema
        )

    @_async_trace_method
    async def async_poll_job(
        self,
        study_key: str,
        batch_id: str,
        *,
        interval: int = 5,
        timeout: int = 300,
    ) -> JobStatus:
        """Asynchronously poll a job until it reaches a terminal state."""
        fetch_result = getattr(self, "_async_client", None) and getattr(
            self._async_client, "get", None
        )
        from typing import cast

        return cast(
            JobStatus,
            await AsyncJobPoller(self.jobs.async_get).run(study_key, batch_id, interval, timeout),
        )


SDKConvenienceMixin = SyncSDKConvenienceMixin
