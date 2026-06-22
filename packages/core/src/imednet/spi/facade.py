"""TODO: Add docstring."""
from typing import Any, List, Optional, Protocol, Union

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


class ImednetFacade(Protocol):
    """TODO: Add docstring."""
    def get_codings(self, study_key: str, **filters: FilterValue) -> List[Coding]:
        """TODO: Add docstring."""
        ...
    def get_forms(self, study_key: str, **filters: FilterValue) -> List[Form]:
        """TODO: Add docstring."""
        ...
    def get_intervals(self, study_key: str, **filters: FilterValue) -> List[Interval]:
        """TODO: Add docstring."""
        ...
    def get_job(self, study_key: str, batch_id: str) -> JobStatus:
        """TODO: Add docstring."""
        ...
    def get_queries(self, study_key: str, **filters: FilterValue) -> List[Query]:
        """TODO: Add docstring."""
        ...
    def get_record_revisions(
        self, study_key: str, **filters: FilterValue
    ) -> List[RecordRevision]:
        """TODO: Add docstring."""
        ...
    def get_records(self, study_key: str, **filters: FilterValue) -> List[Record]:
        """TODO: Add docstring."""
        ...
    def get_sites(self, study_key: str, **filters: FilterValue) -> List[Site]:
        """TODO: Add docstring."""
        ...
    def get_studies(self, **filters: FilterValue) -> List[Study]:
        """TODO: Add docstring."""
        ...
    def get_subjects(self, study_key: str, **filters: FilterValue) -> List[Subject]:
        """TODO: Add docstring."""
        ...
    def get_users(self, study_key: str, **filters: FilterValue) -> List[User]:
        """TODO: Add docstring."""
        ...
    def get_variables(self, study_key: str, **filters: FilterValue) -> List[Variable]:
        """TODO: Add docstring."""
        ...
    def get_visits(self, study_key: str, **filters: FilterValue) -> List[Visit]:
        """TODO: Add docstring."""
        ...
    def create_record(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Any = None,
    ) -> Job:
        """TODO: Add docstring."""
        ...
    def poll_job(
        self, study_key: str, batch_id: str, timeout: float = 300.0, interval: float = 2.0
    ) -> JobStatus:
        """TODO: Add docstring."""
        ...

    @property
    def auth(self) -> Any:
        """TODO: Add docstring."""
        ...


class AsyncImednetFacade(Protocol):
    """TODO: Add docstring."""
    async def async_get_codings(self, study_key: str, **filters: FilterValue) -> List[Coding]:
        """TODO: Add docstring."""
        ...
    async def async_get_forms(self, study_key: str, **filters: FilterValue) -> List[Form]:
        """TODO: Add docstring."""
        ...
    async def async_get_intervals(
        self, study_key: str, **filters: FilterValue
    ) -> List[Interval]:
        """TODO: Add docstring."""
        ...
    async def async_get_job(self, study_key: str, batch_id: str) -> JobStatus:
        """TODO: Add docstring."""
        ...
    async def async_get_queries(self, study_key: str, **filters: FilterValue) -> List[Query]:
        """TODO: Add docstring."""
        ...
    async def async_get_record_revisions(
        self, study_key: str, **filters: FilterValue
    ) -> List[RecordRevision]:
        """TODO: Add docstring."""
        ...
    async def async_get_records(self, study_key: str, **filters: FilterValue) -> List[Record]:
        """TODO: Add docstring."""
        ...
    async def async_get_sites(self, study_key: str, **filters: FilterValue) -> List[Site]:
        """TODO: Add docstring."""
        ...
    async def async_get_studies(self, **filters: FilterValue) -> List[Study]:
        """TODO: Add docstring."""
        ...
    async def async_get_subjects(self, study_key: str, **filters: FilterValue) -> List[Subject]:
        """TODO: Add docstring."""
        ...
    async def async_get_users(self, study_key: str, **filters: FilterValue) -> List[User]:
        """TODO: Add docstring."""
        ...
    async def async_get_variables(
        self, study_key: str, **filters: FilterValue
    ) -> List[Variable]:
        """TODO: Add docstring."""
        ...
    async def async_get_visits(self, study_key: str, **filters: FilterValue) -> List[Visit]:
        """TODO: Add docstring."""
        ...
    async def async_create_record(
        self,
        study_key: str,
        records_data: List[JsonDict],
        email_notify: Union[bool, str, None] = None,
        *,
        schema: Any = None,
    ) -> Job:
        """TODO: Add docstring."""
        ...
    async def async_poll_job(
        self, study_key: str, batch_id: str, timeout: float = 300.0, interval: float = 2.0
    ) -> JobStatus:
        """TODO: Add docstring."""
        ...
