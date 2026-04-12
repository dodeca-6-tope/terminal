"""Scrollbar — visual indicator for scroll position."""

from __future__ import annotations

from collections.abc import Callable

from ttyz.components.base import Renderable, frame
from ttyz.components.scroll import ScrollState
from ttyz.style import dim

ScrollbarFn = Callable[[int, int, int], list[str]]


def scrollbar_default(h: int, total: int, offset: int) -> list[str]:
    """Default scrollbar: heavy line thumb with half-cell resolution, dim track."""
    if total <= h:
        return [""] * h
    h2 = h * 2
    thumb2 = max(2, h2 * h // total)
    max_off = total - h
    top2 = offset * (h2 - thumb2) // max_off if max_off > 0 else 0
    bot2 = top2 + thumb2
    return ["┃" if i * 2 < bot2 and (i + 1) * 2 > top2 else dim("│") for i in range(h)]


def scrollbar(
    state: ScrollState,
    render_fn: ScrollbarFn = scrollbar_default,
    width: str | None = "1",
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    def render(w: int, h: int | None = None) -> list[str]:
        sh = state.height
        if sh <= 0 or state.total <= sh:
            return [""] * (sh or 0)
        return render_fn(sh, state.total, state.offset)

    return frame(Renderable(render, 1, 1), width, height, grow, bg, overflow)
