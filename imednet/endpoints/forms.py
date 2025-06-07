"""Endpoint for managing forms (eCRFs) in a study."""

from typing import Any, List, Optional, cast

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.forms import Form


class FormsEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with forms (eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual forms.
    """

    path = "/api/v1/edc/studies"

    def list(
        self,
        study_key: Optional[str] = None,
        page_size: Optional[int] = None,
        **filters: Any,
    ) -> List[Form]:
        """
        List forms in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            ``**filters``: Additional filter parameters

        Returns:
            List of Form objects
        """
        paginator = cast(
            Paginator,
            build_paginator(
                self,
                Paginator,
                "forms",
                study_key,
                page_size,
                filters,
            ),
        )
        return [Form.from_json(item) for item in paginator]

    def get(self, study_key: str, form_id: int) -> Form:
        """
        Get a specific form by ID.

        Args:
            study_key: Study identifier
            form_id: Form identifier

        Returns:
            Form object
        """
        path = self._build_path(study_key, "forms", form_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Form {form_id} not found in study {study_key}")
        return Form.from_json(raw[0])
