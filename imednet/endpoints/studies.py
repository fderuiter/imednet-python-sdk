"""Endpoint for managing studies in the iMedNet system."""

from typing import Any, List, Optional, cast

from imednet.core.client import Client
from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.studies import Study


class StudiesEndpoint(BaseEndpoint[Client]):
    """
    API endpoint for interacting with studies in the iMedNet system.

    Provides methods to list available studies and retrieve specific studies.
    """

    path = "/api/v1/edc/studies"

    def list(
        self,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Study]:
        """
        List studies with optional filtering.

        Args:
            ``**filters``: Filter parameters

        Returns:
            List of Study objects
        """
        paginator = cast(
            Paginator,
            build_paginator(
                self,
                Paginator,
                "",
                None,
                page_size,
                filters,
                require_study=False,
            ),
        )
        return [Study.model_validate(item) for item in paginator]

    def get(self, study_key: str) -> Study:
        """
        Get a specific study by key.

        Args:
            study_key: Study identifier

        Returns:
            Study object
        """
        path = self._build_path(study_key)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Study {study_key} not found")
        return Study.model_validate(raw[0])
