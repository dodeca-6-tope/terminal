"""Scrollbar — visual indicator for scroll position."""

from __future__ import annotations

from collections.abc import Callable

from terminal.components.base import Component
from terminal.components.scroll import ScrollState
from terminal.style import dim

ScrollbarFn = Callable[[int, int, int], list[str]]


def scrollbar_default(h: int, total: int, offset: int) -> list[str]:
    """Default scrollbar: heavy line thumb with half-cell resolution, dim track."""
    if total <= h:
        return [""] * h
    h2 = h * 2
    thumb2 = max(2, h2 * h // total)
    track2 = h2 - thumb2
    max_off = total - h
    top2 = offset * track2 // max_off if max_off > 0 else 0
    bot2 = top2 + thumb2

    col: list[str] = []
    for i in range(h):
        upper = i * 2
        lower = upper + 1
        if top2 <= upper < bot2 or top2 <= lower < bot2:
            col.append("┃")
        else:
            col.append(dim("│"))
    return col


class Scrollbar(Component):
    """Scrollbar that reads from a ScrollState. Compose alongside Scroll."""

    def __init__(
        self,
        state: ScrollState,
        render_fn: ScrollbarFn = scrollbar_default,
    ) -> None:
        self._state = state
        self._render_fn = render_fn

    def flex_basis(self) -> int:
        return 1

    def flex_grow_height(self) -> bool:
        return True

    def render(self, width: int, height: int | None = None) -> list[str]:
        h = self._state.height
        if h <= 0 or self._state.total <= h:
            return [""] * (h or 0)
        return self._render_fn(h, self._state.total, self._state.offset)


def scrollbar(
    state: ScrollState,
    render_fn: ScrollbarFn = scrollbar_default,
) -> Scrollbar:
    return Scrollbar(state, render_fn=render_fn)
