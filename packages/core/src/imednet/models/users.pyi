from datetime import datetime
from typing import Any, Optional, Dict, List
from imednet.models.json_base import JsonModel

class User(JsonModel):
    user_id: Optional[str]
    login: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    user_active_in_study: Optional[bool]

