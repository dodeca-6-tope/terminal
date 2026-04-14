"""Text component — renders strings with optional truncation, wrap, padding."""

from __future__ import annotations

from ttyz.components.base import Renderable
from ttyz.ext import TextRender


def text(
    value: object = "",
    *,
    wrap: bool = False,
    truncation: str | None = None,
    padding: int = 0,
    padding_left: int | None = None,
    padding_right: int | None = None,
    width: str | None = None,
    height: str | None = None,
    grow: int | None = None,
    bg: int | None = None,
    overflow: str = "visible",
) -> Renderable:
    pl = padding if padding_left is None else padding_left
    pr = padding if padding_right is None else padding_right

    tr = TextRender(value, truncation, pl, pr, wrap)
    basis = tr.visible_w + pl + pr

    return Renderable(
        tr, basis, grow or 0, width=width, height=height, bg=bg, overflow=overflow
    )
