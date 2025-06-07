"""Endpoint for managing sites (study locations) in a study."""

from typing import Any, List, Optional, cast

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.sites import Site


class SitesEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with sites (study locations) in an iMedNet study.

    Provides methods to list and retrieve individual sites.
    """

    path = "/api/v1/edc/studies"

    def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Site]:
        """
        List sites in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            ``**filters``: Additional filter parameters

        Returns:
            List of Site objects
        """
        paginator = cast(
            Paginator,
            build_paginator(
                self,
                Paginator,
                "sites",
                study_key,
                page_size,
                filters,
            ),
        )
        return [Site.from_json(item) for item in paginator]

    def get(self, study_key: str, site_id: int) -> Site:
        """
        Get a specific site by ID.

        Args:
            study_key: Study identifier
            site_id: Site identifier

        Returns:
            Site object
        """
        path = self._build_path(study_key, "sites", site_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Site {site_id} not found in study {study_key}")
        return Site.from_json(raw[0])
