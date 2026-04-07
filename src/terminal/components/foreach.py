"""Foreach component — render a list of items."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

from terminal.components.base import Renderable, frame

T = TypeVar("T")


def foreach(
    items: Sequence[T],
    render_fn: Callable[[T, int], Renderable],
    width: str | None = None,
    height: str | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    children = [render_fn(item, i) for i, item in enumerate(items)]

    basis = max((c.flex_basis for c in children), default=0)
    grow_w = max((c.flex_grow_width for c in children), default=0)
    grow_h = max((c.flex_grow_height for c in children), default=0)

    def render(w: int, h: int | None = None) -> list[str]:
        lines: list[str] = []
        for child in children:
            lines.extend(child.render(w, h))
        return lines

    return frame(Renderable(render, basis, grow_w, grow_h), width, height, bg, overflow)
