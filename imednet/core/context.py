from dataclasses import dataclass


@dataclass
class Context:
    study_key: str | None = None
    sponsor_key: str | None = None
