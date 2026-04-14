"""Display-width measurement and ANSI-aware string utilities."""

from __future__ import annotations

import re
from functools import lru_cache

from ttyz.buffer import c_display_width
from ttyz.buffer import char_width as char_width
from ttyz.buffer import distribute as distribute
from ttyz.buffer import slice_at_width as slice_at_width
from ttyz.buffer import strip_ansi as strip_ansi
from ttyz.buffer import truncate as truncate

ANSI_RE = re.compile(r"\033\[[^@-~]*[@-~]")

_cached = lru_cache(maxsize=4096)(c_display_width)


def display_width(s: str) -> int:
    if len(s) < 512:
        return _cached(s)
    return c_display_width(s)
