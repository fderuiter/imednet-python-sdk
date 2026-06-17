from datetime import datetime
from typing import Any, Dict, List, Optional

from imednet.models.json_base import JsonModel

class User(JsonModel):
    user_id: Optional[str]
    login: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    user_active_in_study: Optional[bool]

class Role(JsonModel):
    role_id: Optional[str]
    name: Optional[str]
    description: Optional[str]
    level: Optional[int]
    type: Optional[str]
    inactive: Optional[bool]
    community_id: Optional[int]
    date_created: Optional[str]
    date_modified: Optional[str]
