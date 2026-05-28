from __future__ import annotations

from imednet.models.engine import ModelEngine

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.json_base import JsonModel


class QueryComment(JsonModel):
    """A comment or response within a data query thread."""


    pass


QueryComment = ModelEngine.get_model('QueryComment', QueryComment)

class Query(JsonModel):
    """Represents a data query (discrepancy) raised on a record."""


    pass
Query = ModelEngine.get_model('Query', Query)

