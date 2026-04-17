"""Toast — timed message queue."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Literal, TypeAlias

Level: TypeAlias = Literal["info", "warning", "error"]


@dataclass
class Message:
    text: str
    level: Level = "info"


class ToastState:
    """Queue of timed messages. Expired messages are pruned automatically."""

    def __init__(self, ttl: float = 3) -> None:
        self._ttl = ttl
        self._items: list[tuple[Message, float]] = []

    def show(
        self, text: str, level: Level = "info", duration: float | None = None
    ) -> None:
        deadline = time.monotonic() + (duration if duration is not None else self._ttl)
        self._items.insert(0, (Message(text, level), deadline))

    def active(self) -> list[Message]:
        now = time.monotonic()
        self._items = [(m, dl) for m, dl in self._items if now < dl]
        return [m for m, _ in self._items]

    @property
    def visible(self) -> bool:
        return bool(self.active())
