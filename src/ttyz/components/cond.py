"""Conditional rendering component."""

from __future__ import annotations

from ttyz.components.base import Renderable


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

    return Renderable(
        child.render,
        child.flex_basis,
        grow if grow is not None else child.grow,
        width=width,
        height=height,
        bg=bg,
        overflow=overflow,
    )
