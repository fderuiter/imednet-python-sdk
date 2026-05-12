"""Endpoint for managing codings (medical coding) in a study."""

from imednet.core.endpoint.edc_mixin import EdcGenericListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.codings import Coding


class CodingsEndpoint(EdcGenericListGetEndpoint[Coding]):
    """
    API endpoint for interacting with codings (medical coding) in an iMedNet study.

    Provides methods to list and retrieve individual codings.
    """

    PATH = "codings"
    MODEL = Coding
    _id_param = "codingId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()
