"""Toast — timed message buffer."""

from __future__ import annotations

import time


class Toast:
    """A message with a deadline. Check `visible` to decide whether to show it."""

    def __init__(self) -> None:
        self.message = ""
        self._until = 0.0

    def show(self, message: str, duration: float = 2) -> None:
        self.message = message
        self._until = time.monotonic() + duration

    @property
    def visible(self) -> bool:
        return time.monotonic() < self._until
