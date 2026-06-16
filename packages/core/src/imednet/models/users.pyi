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
    name: Optional[str]

class Role(JsonModel):
    role_id: Optional[int]
    role_name: Optional[str]
    system_role: Optional[bool]
    date_created: Optional[str]
    date_modified: Optional[str]
