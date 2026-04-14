"""Foreach component — render a list of items."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

from ttyz.components.base import Renderable

T = TypeVar("T")


def foreach(
    items: Sequence[T],
    render_fn: Callable[[T, int], Renderable],
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    children = [render_fn(item, i) for i, item in enumerate(items)]

    basis = max((c.flex_basis for c in children), default=0)

    def render(w: int, h: int | None = None) -> list[str]:
        lines: list[str] = []
        for child in children:
            lines.extend(child.render(w, h))
            if h is not None and len(lines) >= h:
                return lines[:h]
        return lines

    return Renderable(
        render, basis, grow or 0, width=width, height=height, bg=bg, overflow=overflow
    )
