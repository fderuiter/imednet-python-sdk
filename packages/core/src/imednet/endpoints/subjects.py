"""Endpoint for managing subjects in a study."""

from typing import Awaitable, List, Union, overload

from imednet.core.endpoint.edc_mixin import ClientT, EdcListGetEndpoint
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.subjects import Subject


class SubjectsOperationDef:
    """TODO: Add docstring."""

    PATH = "subjects"
    MODEL = Subject
    _id_param = "subjectKey"


class SubjectsEndpoint(SubjectsOperationDef, EdcListGetEndpoint[Subject, ClientT]):  # type: ignore[misc]
    """TODO: Add docstring."""

    @overload
    def list_by_site(self: "SubjectsEndpoint[RequestorProtocol]", study_key: str, site_id: str | int) -> List[Subject]: ...

    @overload
    def list_by_site(self: "SubjectsEndpoint[AsyncRequestorProtocol]", study_key: str, site_id: str | int) -> Awaitable[List[Subject]]: ...

    def list_by_site(self, study_key: str, site_id: str | int) -> Union[List[Subject], Awaitable[List[Subject]]]:
        """TODO: Add docstring."""
        if self._async_client:
            async def _async_wrapper() -> List[Subject]:
                return [item async for item in self.list(study_key=study_key, site_id=site_id)]  # type: ignore
            return _async_wrapper()
        else:
            return list(self.list(study_key=study_key, site_id=site_id))  # type: ignore

    # Provide backwards compatibility for those explicitly calling async_list_by_site
    def async_list_by_site(self, study_key: str, site_id: str | int) -> Awaitable[List[Subject]]:
        """Alias for list_by_site()."""
        import warnings
        warnings.warn("async_list_by_site is deprecated, use list_by_site()", DeprecationWarning, stacklevel=2)
        return self.list_by_site(study_key=study_key, site_id=site_id)  # type: ignore

class AsyncSubjectsEndpoint(SubjectsEndpoint):  # type: ignore[misc]
    """Legacy backwards-compatible async endpoint."""
    def __init__(self, client, ctx=None):
        """TODO: Add docstring."""
        super().__init__(client, ctx=ctx)
        self._async_client = client
