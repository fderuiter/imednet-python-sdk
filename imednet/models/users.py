from dataclasses import dataclass
from typing import List


@dataclass
class Role:
    date_created: list[int]
    date_modified: list[int]
    role_id: str
    community_id: int
    name: str
    description: str
    level: int
    type: str
    inactive: bool


@dataclass
class User:
    user_id: str
    login: str
    first_name: str
    last_name: str
    email: str
    user_active_in_study: bool
    roles: List[Role]
