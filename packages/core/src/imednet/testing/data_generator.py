"""Internal utility for generating synthetic data without external dependencies."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

class RandomDataGenerator:
    """A deterministic, standard-library based data generator replacement for Faker."""
    
    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def uuid4(self) -> str:
        if self._rng is random._inst:
            return str(uuid.uuid4())
        return str(uuid.UUID(int=self._rng.getrandbits(128), version=4))

    def random_int(self, min: int = 0, max: int = 9999) -> int:
        return self._rng.randint(min, max)

    def pyfloat(self, left_digits: int = 2, right_digits: int = 2, positive: bool = True) -> float:
        min_v = 0.0 if positive else -(10 ** left_digits)
        max_v = float(10 ** left_digits)
        return round(self._rng.uniform(min_v, max_v), right_digits)

    def boolean(self) -> bool:
        return self._rng.choice([True, False])
        
    def random_element(self, elements: List[Any]) -> Any:
        return self._rng.choice(elements)

    def bothify(self, text: str) -> str:
        out = []
        for c in text:
            if c == '?':
                out.append(self._rng.choice('abcdefghijklmnopqrstuvwxyz'))
            elif c == '#':
                out.append(str(self._rng.randint(0, 9)))
            else:
                out.append(c)
        return "".join(out)

    def lexify(self, text: str) -> str:
        return self.bothify(text)

    def company(self) -> str:
        return self._rng.choice(["Acme Corp", "Globex", "Initech", "Umbrella Corp", "Stark Industries"])

    def word(self) -> str:
        return self._rng.choice(["test", "mock", "fake", "sample", "data", "example"])

    def sentence(self, nb_words: int = 3) -> str:
        words = [self.word() for _ in range(nb_words)]
        words[0] = words[0].title()
        return " ".join(words) + "."
        
    def paragraph(self, nb_sentences: int = 3) -> str:
        return " ".join(self.sentence(3) for _ in range(nb_sentences))

    def user_name(self) -> str:
        return self.lexify("?????") + str(self.random_int(10, 99))

    def first_name(self) -> str:
        return self._rng.choice(["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"])

    def last_name(self) -> str:
        return self._rng.choice(["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis"])

    def email(self) -> str:
        return f"{self.first_name().lower()}.{self.last_name().lower()}@{self.lexify('????')}.com"

    def date_time(self) -> datetime:
        days = self._rng.randint(0, 365)
        return datetime.now(timezone.utc) - timedelta(days=days)

generator = RandomDataGenerator()
