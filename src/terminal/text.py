"""ANSI-aware text — a string that knows its visible width."""

import re
from wcwidth import wcswidth

_ANSI_RE = re.compile(r"\033\[[^m]*m")


class Text:
    """A string that measures and manipulates by visible width, ignoring ANSI escapes."""

    __slots__ = ("_raw", "_visible")

    def __init__(self, value=""):
        self._raw = str(value)
        stripped = _ANSI_RE.sub("", self._raw)
        w = wcswidth(stripped)
        self._visible = w if w >= 0 else len(stripped)

    def __len__(self):
        return self._visible

    def __str__(self):
        return self._raw

    def __repr__(self):
        return f"Text({self._raw!r})"

    def __add__(self, other):
        if isinstance(other, Text):
            return Text(self._raw + other._raw)
        return Text(self._raw + str(other))

    def __radd__(self, other):
        return Text(str(other) + self._raw)

    def __format__(self, format_spec):
        return self._raw.__format__(format_spec)

    def truncate(self, max_len: int = 30) -> "Text":
        if self._visible <= max_len:
            return self
        raw = _ANSI_RE.sub("", self._raw)
        return Text(raw[:max_len - 1] + "…")

    def pad(self, width: int, align: str = "left") -> "Text":
        gap = width - self._visible
        if gap <= 0:
            return self
        spaces = " " * gap
        if align == "left":
            return Text(self._raw + spaces)
        return Text(spaces + self._raw)
