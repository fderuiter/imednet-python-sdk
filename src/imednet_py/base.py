from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class IMNModel(BaseModel):
    """Base model with snake_case attribute names and camelCase aliases."""

    model_config = ConfigDict(populate_by_name=True)
