"""Display-width measurement — ANSI-aware, wide-char-aware."""

import re
from functools import lru_cache

from terminal._buffer import char_width as _cwidth
from terminal._buffer import display_width as _c_display_width

ANSI_RE = re.compile(r"\033\[[^@-~]*[@-~]")


@lru_cache(maxsize=4096)
def _cached_display_width(s: str) -> int:
    return _c_display_width(s)


def display_width(s: str) -> int:
    if len(s) < 512:
        return _cached_display_width(s)
    return _c_display_width(s)


def strip_ansi(s: str) -> str:
    if "\033" not in s:
        return s
    return ANSI_RE.sub("", s)


def char_width(ch: str) -> int:
    """Display width of a single character."""
    return _cwidth(ch)


def distribute(total: int, weights: list[int]) -> list[int]:
    """Distribute total proportionally among weighted slots."""
    if not weights:
        return []
    total_weight = sum(weights)
    cum_weight = 0
    cum_space = 0
    sizes: list[int] = []
    for w in weights:
        cum_weight += w
        target = total * cum_weight // total_weight
        sizes.append(target - cum_space)
        cum_space = target
    return sizes


def slice_at_width(s: str, max_width: int) -> str:
    """Slice a plain string to fit within max_width display columns."""
    if s.isascii():
        return s[:max_width]
    w = 0
    for i, ch in enumerate(s):
        cw = char_width(ch)
        if w + cw > max_width:
            return s[:i]
        w += cw
    return s
