import time
from dataclasses import dataclass
from typing import Literal

Level = Literal["info", "error", "warning", "success"]

_DEFAULT_TTL = 3


@dataclass
class Notification:
    text: str
    level: Level


class Notifications:
    def __init__(self, ttl: float = _DEFAULT_TTL):
        self._ttl = ttl
        self._items: list[tuple[Notification, float]] = []

    def add(self, text: str, level: Level = "info"):
        self._items.insert(0, (Notification(text, level), time.monotonic()))

    def active(self) -> list[Notification]:
        now = time.monotonic()
        self._items = [(n, ts) for n, ts in self._items if now - ts < self._ttl]
        return [n for n, _ in self._items]
