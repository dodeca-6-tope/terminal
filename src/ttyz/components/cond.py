"""Conditional rendering component."""

from __future__ import annotations

from ttyz.components.base import Renderable, frame


def cond(
    condition: object,
    child: Renderable,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    if not condition:

        def _empty(w: int, h: int | None = None) -> list[str]:
            return []

        return Renderable(_empty)

    return frame(child, width, height, grow, bg, overflow)
