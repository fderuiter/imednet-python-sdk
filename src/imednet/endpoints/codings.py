"""Endpoint for managing codings (medical coding) in a study."""

from imednet.core.endpoint.base import GenericListGetEndpoint
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.endpoint.mixins import KeyErrorPopStudyKeyMixin
from imednet.models.codings import Coding


class CodingsEndpoint(
    EdcEndpointMixin,
    KeyErrorPopStudyKeyMixin,
    GenericListGetEndpoint[Coding],
):
    """
    API endpoint for interacting with codings (medical coding) in an iMedNet study.

    Provides methods to list and retrieve individual codings.
    """

    PATH = "codings"
    MODEL = Coding
    _id_param = "codingId"
