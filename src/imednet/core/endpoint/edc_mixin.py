"""EDC-specific endpoint base class and mixin."""

from __future__ import annotations

from typing import Any, Dict, Optional, TypeVar

from imednet.core.context import get_study_context
from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class EdcEndpointMixin:
    """
    Mixin providing EDC-specific logic for endpoints.

    This includes the base path for EDC resources and automatic injection
    of the default study key into filters.
    """

    BASE_PATH = "/api/v1/edc/studies"

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject default studyKey if missing.

        Args:
            filters: The current dictionary of filters.

        Returns:
            The filters dictionary with studyKey injected if applicable.
        """
        study_key = get_study_context()
        if "studyKey" not in filters and study_key:
            filters["studyKey"] = study_key
        return filters


class EdcGenericListGetEndpoint(GenericListGetEndpoint[T]):
    """
    Single base class for EDC API endpoints with list and get operations.

    Combines the EDC-specific path prefix and automatic study-key injection
    with the full list/get composition provided by
    :class:`~imednet.core.endpoint.base.GenericListGetEndpoint`.

    Concrete endpoints should inherit **only** from this class (plus the
    generic type parameter) and declare ``PATH``, ``MODEL``, and any
    overrides as class attributes:

    .. code-block:: python

        class RecordsEndpoint(EdcGenericListGetEndpoint[Record]):
            PATH = "records"
            MODEL = Record
            _id_param = "recordId"
    """

    BASE_PATH = "/api/v1/edc/studies"

    def __init__(
        self,
        client: RequestorProtocol,
        ctx: object | None = None,
        async_client: Optional[AsyncRequestorProtocol] = None,
    ) -> None:
        super().__init__(client, ctx, async_client)

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject the default study key from context if not already present.

        Args:
            filters: The current dictionary of filters.

        Returns:
            The filters dictionary with studyKey injected if applicable.
        """
        study_key = get_study_context()
        if "studyKey" not in filters and study_key:
            filters["studyKey"] = study_key
        return filters
